"""LLM Judge 评估：三模型盲评对比。"""
import json
import os
import random
import yaml
import torch
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", "..", "backend", ".env"))
from openai import OpenAI
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)
from peft import PeftModel

# llm_model/ 目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve(path: str) -> str:
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(PROJECT_DIR, path))


def load_config() -> dict:
    config_path = os.path.join(PROJECT_DIR, "config", "train_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_models(config: dict) -> dict:
    model_cfg = config["model"]
    qlora_cfg = config["qlora"]
    output_cfg = config["output"]

    tokenizer = AutoTokenizer.from_pretrained(model_cfg["name"], trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=qlora_cfg["load_in_4bit"],
        bnb_4bit_compute_dtype=getattr(torch, qlora_cfg["bnb_4bit_compute_dtype"]),
        bnb_4bit_quant_type=qlora_cfg["bnb_4bit_quant_type"],
    )

    base_model = AutoModelForCausalLM.from_pretrained(
        model_cfg["name"], quantization_config=bnb_config, device_map="auto",
        trust_remote_code=True,
    )

    sft_model = AutoModelForCausalLM.from_pretrained(
        model_cfg["name"], quantization_config=bnb_config, device_map="auto",
        trust_remote_code=True,
    )
    sft_model = PeftModel.from_pretrained(sft_model, _resolve(output_cfg["sft_adapter"]))

    grpo_model = AutoModelForCausalLM.from_pretrained(
        model_cfg["name"], quantization_config=bnb_config, device_map="auto",
        trust_remote_code=True,
    )
    grpo_model = PeftModel.from_pretrained(grpo_model, _resolve(output_cfg["grpo_adapter"]))

    return {
        "base": (base_model, tokenizer),
        "sft": (sft_model, tokenizer),
        "grpo": (grpo_model, tokenizer),
    }


def generate(model, tokenizer, prompt: str, max_new_tokens: int = 256) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    outputs = model.generate(
        **inputs, max_new_tokens=max_new_tokens, do_sample=True,
        temperature=0.7, top_p=0.9,
        pad_token_id=tokenizer.pad_token_id,
    )
    return tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
    )


def judge(character_card: dict, test_prompt: str, response_a: str, response_b: str) -> dict:
    client = OpenAI(api_key=os.getenv("API_KEY"), base_url=os.getenv("API_BASE"))
    judge_prompt = f"""你是一个角色扮演对话评估裁判。根据角色设定，对两条回复打分。

【角色设定】
角色名：{character_card['name']}
性格：{character_card['personality']}
背景：{character_card['background']}
说话风格：{character_card['speaking_style']}

【测试问题】
{test_prompt}

【回复A】
{response_a}

【回复B】
{response_b}

从以下维度分别打分（1-5分整数）：
1. 角色一致性：回复是否符合角色设定的性格、背景、说话风格
2. 对话流畅性：语言是否自然、连贯、不生硬

只返回 JSON 格式：{{"A": {{"一致性": X, "流畅性": Y}}, "B": {{"一致性": X, "流畅性": Y}}}}"""

    response = client.chat.completions.create(
        model=os.getenv("MODEL", "deepseek-v4-pro"),
        messages=[{"role": "user", "content": judge_prompt}],
        temperature=0.1,
    )
    result_text = response.choices[0].message.content.strip()
    if result_text.startswith("```"):
        result_text = result_text[result_text.find("\n"):result_text.rfind("```")].strip()
    return json.loads(result_text)


def eval_compare(max_samples: int = None):
    config = load_config()
    card_path = os.path.join(PROJECT_DIR, "data", "character_card.json")
    with open(card_path, "r", encoding="utf-8") as f:
        character_card = json.load(f)

    test_path = os.path.join(PROJECT_DIR, "data", "test_prompts.json")
    with open(test_path, "r", encoding="utf-8") as f:
        test_prompts = json.load(f)

    if max_samples:
        test_prompts = test_prompts[:max_samples]

    print("Loading models...")
    models = load_models(config)

    comparisons = [
        ("base_vs_sft", "base", "sft"),
        ("sft_vs_grpo", "sft", "grpo"),
        ("base_vs_grpo", "base", "grpo"),
    ]
    results = {key: [] for key, _, _ in comparisons}

    for i, tp in enumerate(test_prompts):
        prompt = tp["prompt"]
        print(f"\n[{i+1}/{len(test_prompts)}] {prompt[:50]}...")

        # 生成三个模型的回复（缓存避免重复生成）
        responses = {}
        for model_name in ["base", "sft", "grpo"]:
            if model_name not in responses:
                resp = generate(*models[model_name], prompt)
                responses[model_name] = resp

        for comp_key, model_a, model_b in comparisons:
            resp_a = responses[model_a]
            resp_b = responses[model_b]
            if random.random() < 0.5:
                judge_result = judge(character_card, prompt, resp_a, resp_b)
                results[comp_key].append({
                    "prompt": prompt,
                    "model_A": model_a, "model_B": model_b,
                    "scores": judge_result,
                })
            else:
                judge_result = judge(character_card, prompt, resp_b, resp_a)
                swapped = {"A": judge_result["B"], "B": judge_result["A"]}
                results[comp_key].append({
                    "prompt": prompt,
                    "model_A": model_a, "model_B": model_b,
                    "scores": swapped,
                })

    print_summary(results)
    save_report(results, character_card)


def print_summary(results: dict):
    print("\n" + "=" * 60)
    print("LLM Judge 评估结果")
    print("=" * 60)
    for comp_key, items in results.items():
        a_c = sum(r["scores"]["A"]["一致性"] for r in items) / len(items)
        a_f = sum(r["scores"]["A"]["流畅性"] for r in items) / len(items)
        b_c = sum(r["scores"]["B"]["一致性"] for r in items) / len(items)
        b_f = sum(r["scores"]["B"]["流畅性"] for r in items) / len(items)
        b_wins = sum(1 for r in items
            if r["scores"]["B"]["一致性"] + r["scores"]["B"]["流畅性"]
            > r["scores"]["A"]["一致性"] + r["scores"]["A"]["流畅性"])
        a_wins = sum(1 for r in items
            if r["scores"]["A"]["一致性"] + r["scores"]["A"]["流畅性"]
            > r["scores"]["B"]["一致性"] + r["scores"]["B"]["流畅性"])
        ties = len(items) - a_wins - b_wins
        a_name = items[0]["model_A"].upper()
        b_name = items[0]["model_B"].upper()
        print(f"\n{comp_key}:")
        print(f"  {a_name}: 一致性={a_c:.2f}, 流畅性={a_f:.2f}")
        print(f"  {b_name}: 一致性={b_c:.2f}, 流畅性={b_f:.2f}")
        print(f"  胜率: {b_name}胜 {b_wins}/{len(items)} ({100*b_wins/len(items):.0f}%), "
              f"平局 {ties}")


def save_report(results: dict, character_card: dict):
    report_path = os.path.join(os.path.dirname(__file__), "eval_report.md")
    lines = [
        f"# GRPO + QLoRA 微调评估报告\n",
        f"**角色**: {character_card['name']}\n\n",
        "## 综合指标\n",
    ]
    for comp_key, items in results.items():
        a_name = items[0]["model_A"].upper()
        b_name = items[0]["model_B"].upper()
        a_c = sum(r["scores"]["A"]["一致性"] for r in items) / len(items)
        a_f = sum(r["scores"]["A"]["流畅性"] for r in items) / len(items)
        b_c = sum(r["scores"]["B"]["一致性"] for r in items) / len(items)
        b_f = sum(r["scores"]["B"]["流畅性"] for r in items) / len(items)
        lines.append(f"### {comp_key}\n")
        lines.append(f"| 模型 | 角色一致性 | 对话流畅性 |\n")
        lines.append(f"|------|-----------|----------|\n")
        lines.append(f"| {a_name} | {a_c:.2f} | {a_f:.2f} |\n")
        lines.append(f"| {b_name} | {b_c:.2f} | {b_f:.2f} |\n\n")

    lines.append("\n## 逐条详情\n")
    for comp_key, items in results.items():
        lines.append(f"### {comp_key}\n")
        for i, r in enumerate(items):
            lines.append(f"**Q{i+1}**: {r['prompt'][:60]}...\n")
            lines.append(f"- {r['model_A'].upper()}: 一致性={r['scores']['A']['一致性']}, "
                         f"流畅性={r['scores']['A']['流畅性']}\n")
            lines.append(f"- {r['model_B'].upper()}: 一致性={r['scores']['B']['一致性']}, "
                         f"流畅性={r['scores']['B']['流畅性']}\n\n")

    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(lines)
    print(f"\n详细报告已保存到 {report_path}")


if __name__ == "__main__":
    eval_compare()
