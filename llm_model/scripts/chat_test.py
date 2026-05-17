"""交互式对话测试：加载微调模型进行多轮对话。"""
import json
import os
import sys
import yaml
import torch
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


def load_model(model_type: str, config: dict):
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

    model = AutoModelForCausalLM.from_pretrained(
        model_cfg["name"],
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )

    if model_type == "sft":
        model = PeftModel.from_pretrained(model, _resolve(output_cfg["sft_adapter"]))
    elif model_type == "grpo":
        model = PeftModel.from_pretrained(model, _resolve(output_cfg["grpo_adapter"]))

    return model, tokenizer


def chat(model, tokenizer, character_card: dict):
    print(f"\n正在与 {character_card['name']} 对话 (输入 'quit' 退出)\n")
    history = []

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() == "quit":
            break

        history.append({"role": "user", "content": user_input})
        system_msg = (
            f"你是{character_card['name']}。"
            f"{character_card['personality']} "
            f"说话风格：{character_card['speaking_style']}"
        )
        messages = [{"role": "system", "content": system_msg}] + history

        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
        outputs = model.generate(
            **inputs, max_new_tokens=256, do_sample=True,
            temperature=0.7, top_p=0.9,
            pad_token_id=tokenizer.pad_token_id,
        )
        response = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
        )
        history.append({"role": "assistant", "content": response})
        print(f"{character_card['name']}: {response}\n")


if __name__ == "__main__":
    config_path = os.path.join(PROJECT_DIR, "config", "train_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    card_path = os.path.join(PROJECT_DIR, "data", "character_card.json")
    with open(card_path, "r", encoding="utf-8") as f:
        character_card = json.load(f)

    if len(sys.argv) > 1:
        model_type = sys.argv[1]
    else:
        model_type = input("选择模型 (base/sft/grpo): ").strip().lower()

    print(f"Loading {model_type} model...")
    model, tokenizer = load_model(model_type, config)
    chat(model, tokenizer, character_card)
