"""调用 deepseek-v4-pro 生成角色扮演对话数据集。"""
import json
import os
import random
import yaml

from openai import OpenAI

# llm_model/ 目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config(config_path: str = None) -> dict:
    if config_path is None:
        config_path = os.path.join(PROJECT_DIR, "config", "train_config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_character_card() -> dict:
    path = os.path.join(PROJECT_DIR, "data", "character_card.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_prompts() -> dict:
    path = os.path.join(PROJECT_DIR, "data", "prompts.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_character_card(card: dict) -> str:
    return (
        f"角色名：{card['name']}\n"
        f"性格：{card['personality']}\n"
        f"背景：{card['background']}\n"
        f"说话风格：{card['speaking_style']}"
    )


def _extract_json(text: str) -> list:
    """从 LLM 返回的文本中提取 JSON 数组，处理常见格式问题。"""
    import re

    text = text.strip()
    # 移除 markdown 代码块包装
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)

    # 尝试直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 尝试提取 JSON 数组
    match = re.search(r"\[.*\]", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # 尝试逐行修复（去除尾部逗号、补全括号）
    # 找到最后一个完整的 object }
    objects = []
    depth = 0
    start = -1
    for i, ch in enumerate(text):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                try:
                    obj = json.loads(text[start : i + 1])
                    objects.append(obj)
                except json.JSONDecodeError:
                    pass
                start = -1

    if objects:
        return objects

    raise ValueError(f"无法从响应中提取 JSON: {text[:200]}...")


def generate_dataset():
    config = load_config()
    cfg = config["data"]
    character_card = load_character_card()
    prompts = load_prompts()

    client = OpenAI(
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("API_BASE"),
    )
    model = os.getenv("MODEL") or cfg["model"]
    train_samples = cfg["train_samples"]
    test_split = cfg["test_split"]

    batch_size = 20
    all_messages = []

    for batch_start in range(0, train_samples, batch_size):
        batch_count = min(batch_size, train_samples - batch_start)
        user_prompt = prompts["generation_prompt"].format(
            count=batch_count,
            character_card=format_character_card(character_card),
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompts["system_prompt"]},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,
        )
        content = response.choices[0].message.content
        batch_data = _extract_json(content)
        all_messages.extend(batch_data)
        print(f"已生成 {min(batch_start + batch_size, train_samples)}/{train_samples} 条")

    random.seed(42)
    random.shuffle(all_messages)
    split_idx = int(len(all_messages) * (1 - test_split))
    train_data = all_messages[:split_idx]
    test_data = all_messages[split_idx:]

    dataset_path = os.path.join(PROJECT_DIR, "data", "dataset.jsonl")
    with open(dataset_path, "w", encoding="utf-8") as f:
        for item in train_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    print(f"训练集已保存: {len(train_data)} 条 -> {dataset_path}")

    test_prompts = []
    for item in test_data:
        user_msgs = [m["content"] for m in item["messages"] if m["role"] == "user"]
        if user_msgs:
            test_prompts.append({"prompt": user_msgs[0]})
    test_path = os.path.join(PROJECT_DIR, "data", "test_prompts.json")
    with open(test_path, "w", encoding="utf-8") as f:
        json.dump(test_prompts, f, ensure_ascii=False, indent=2)
    print(f"测试集已保存: {len(test_prompts)} 条 -> {test_path}")


if __name__ == "__main__":
    generate_dataset()
