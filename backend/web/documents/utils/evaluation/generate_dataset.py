import json
import os
from openai import OpenAI

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def load_chunks_from_lancedb() -> list[dict]:
    """从 LanceDB 读取所有 chunk 的 id 和内容。"""
    import lancedb
    db = lancedb.connect(os.path.join(BASE_DIR, "lancedb_storage"))
    table = db.open_table("my_knowledge_base")
    rows = table.to_pandas()
    return [{"chunk_id": row["id"], "content": row["text"]} for _, row in rows.iterrows()]


def generate_dataset(output_path: str = None) -> dict:
    """遍历所有 chunk，用 LLM 为每个 chunk 生成 2-3 个问句，保存为测试集。

    Args:
        output_path: 输出 JSON 文件路径，默认保存到 evaluation/test_dataset.json

    Returns:
        {"queries": [{"id": "q001", "question": "...", "relevant_chunk_ids": ["chunk_0"]}, ...]}
    """
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "test_dataset.json")

    chunks = load_chunks_from_lancedb()
    client = OpenAI(
        api_key=os.getenv("API_KEY"),
        base_url=os.getenv("API_BASE"),
    )
    model = os.getenv("MODEL", "deepseek-v4-flash")

    queries = []
    for chunk in chunks:
        prompt = f"""你是一个测试数据生成器。下面是一段知识库文档的内容，请生成 2-3 个用户会提出的问题，这些问题要确保原文能作为答案。

要求：
1. 问题自然、口语化，像真实用户会问的
2. 问题必须与原文内容直接相关
3. 输出格式：每行一个问题，不要编号

原文内容：
---
{chunk['content']}
---"""

        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        questions_text = response.choices[0].message.content.strip()
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]

        for q in questions:
            queries.append({
                "question": q,
                "relevant_chunk_ids": [chunk["chunk_id"]],
            })

    # 去重和编号
    seen = set()
    unique_queries = []
    for q in queries:
        if q["question"] not in seen:
            seen.add(q["question"])
            unique_queries.append(q)

    for i, q in enumerate(unique_queries):
        q["id"] = f"q{i:03d}"

    dataset = {"queries": unique_queries}
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"已生成{len(unique_queries)}条测试数据，保存到 {output_path}")
    return dataset
