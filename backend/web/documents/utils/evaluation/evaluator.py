import json
import sys
from pathlib import Path

# 将 backend/ 加入 sys.path 以支持 from web.documents.utils...
_FILE_DIR = Path(__file__).resolve().parent  # evaluation/
_BACKEND_DIR = _FILE_DIR.parent.parent.parent.parent  # 4 级向上 = backend/
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

from web.documents.utils.hybrid_search import hybrid_search, vector_search_only, bm25_search_only


def load_dataset(dataset_path: str) -> list[dict]:
    """载入测试数据集。"""
    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["queries"]


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """前 k 个结果中命中相关文档的比例（占所有相关文档）。"""
    retrieved_k = retrieved_ids[:k]
    hits = len(set(retrieved_k) & set(relevant_ids))
    return hits / len(relevant_ids) if relevant_ids else 0.0


def hit_rate_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """前 k 个结果中至少命中一个相关文档的查询比例。"""
    retrieved_k = set(retrieved_ids[:k])
    relevant_set = set(relevant_ids)
    return 1.0 if retrieved_k & relevant_set else 0.0


def mrr(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """Mean Reciprocal Rank：第一个相关文档排名的倒数。"""
    for i, rid in enumerate(retrieved_ids):
        if rid in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0


def evaluate(queries: list[dict], ks: list[int] = None) -> tuple[dict, list[dict]]:
    """对测试集执行三路检索评估。

    Args:
        queries: [{"id": "q001", "question": "...", "relevant_chunk_ids": [...]}, ...]
        ks: 评估的 k 值列表，默认 [3, 5, 10]

    Returns:
        (summary, details)
        summary: {"vector": {"recall@3": ..., "mrr": ...}, "bm25": {...}, "hybrid": {...}}
        details: [{"id": "q001", "question": "...", "relevant": [...], "vector_ids": [...], "bm25_ids": [...], "hybrid_ids": [...]}, ...]
    """
    if ks is None:
        ks = [3, 5, 10]

    methods: dict[str, callable] = {
        "vector": lambda q: [cid for cid, _ in vector_search_only(q, k=max(ks))],
        "bm25": lambda q: [cid for cid, _ in bm25_search_only(q, k=max(ks))],
        "hybrid": lambda q: [r["chunk_id"] for r in hybrid_search(q, k_vector=10, k_bm25=10, final_k=max(ks))],
    }

    summary: dict[str, dict] = {}
    details: list[dict] = []

    for method_name, search_fn in methods.items():
        all_recall: dict[int, list[float]] = {k: [] for k in ks}
        all_hit_rate: dict[int, list[float]] = {k: [] for k in ks}
        all_mrr: list[float] = []

        for i, query_data in enumerate(queries):
            question: str = query_data["question"]
            relevant: list[str] = query_data["relevant_chunk_ids"]
            retrieved_ids: list[str] = search_fn(question)

            for k in ks:
                all_recall[k].append(recall_at_k(retrieved_ids, relevant, k))
                all_hit_rate[k].append(hit_rate_at_k(retrieved_ids, relevant, k))
            all_mrr.append(mrr(retrieved_ids, relevant))

            # 存储逐查询详情（仅第一个 method 时创建，其余 method 时追加）
            if method_name == "vector":
                details.append({
                    "id": query_data["id"],
                    "question": question,
                    "relevant": relevant,
                    "vector_ids": retrieved_ids,
                })
            else:
                details[i][f"{method_name}_ids"] = retrieved_ids

        method_result: dict[str, float] = {"mrr": sum(all_mrr) / len(all_mrr) if all_mrr else 0.0}
        for k in ks:
            method_result[f"recall@{k}"] = sum(all_recall[k]) / len(all_recall[k]) if all_recall[k] else 0.0
            method_result[f"hit_rate@{k}"] = sum(all_hit_rate[k]) / len(all_hit_rate[k]) if all_hit_rate[k] else 0.0
        summary[method_name] = method_result

    return summary, details


def print_report(results: dict, ks: list[int] = None):
    """打印评估对比报告。"""
    if ks is None:
        ks = [3, 5, 10]

    methods_order = ["vector", "bm25", "hybrid"]
    labels = {"vector": "Vector-only", "bm25": "BM25-only", "hybrid": "Hybrid(RRF)"}

    header_cols = ["Method"] + [f"Recall@{k}" for k in ks] + [f"Hit Rate@{k}" for k in ks] + ["MRR"]
    header = "  ".join(f"{col:<14}" for col in header_cols)
    print(header)
    print("-" * len(header))

    for method in methods_order:
        if method not in results:
            continue
        r = results[method]
        cols = [labels[method]]
        for k in ks:
            cols.append(f"{r.get(f'recall@{k}', 0):.4f}")
        for k in ks:
            cols.append(f"{r.get(f'hit_rate@{k}', 0):.4f}")
        cols.append(f"{r.get('mrr', 0):.4f}")
        row = "  ".join(f"{col:<14}" for col in cols)
        print(row)


def save_report(summary: dict, details: list[dict], ks: list[int] = None, output_path: str = None) -> str:
    """生成 Markdown 评估报告，包含整体指标和逐查询详情。

    Args:
        summary: evaluate() 返回的聚合指标
        details: evaluate() 返回的逐查询详情
        ks: k 值列表
        output_path: 输出路径，默认保存到 evaluation/evaluation_report.md

    Returns:
        报告文件路径
    """
    import os
    from datetime import datetime

    if ks is None:
        ks = [3, 5, 10]
    if output_path is None:
        output_path = os.path.join(os.path.dirname(__file__), "evaluation_report.md")

    methods_order = ["vector", "bm25", "hybrid"]
    labels = {"vector": "Vector-only", "bm25": "BM25-only", "hybrid": "Hybrid(RRF)"}
    detail_k = max(ks)

    # 构建逐查询详情（使用已收集的检索结果，无需重新检索）
    detail_lines = []
    for d in details:
        qid = d["id"]
        question = d["question"]
        relevant = d["relevant"]
        detail_lines.append(f"### {qid}: {question}\n")
        detail_lines.append(f"- **相关文档**: {', '.join(relevant)}\n")

        for method in methods_order:
            retrieved = d.get(f"{method}_ids", [])
            hits = [cid for cid in retrieved[:detail_k] if cid in relevant]
            status = "✅" if hits else "❌"
            display_ids = ', '.join(retrieved[:5])
            detail_lines.append(f"- **{labels[method]} (k={detail_k})**: {status} 命中: {hits if hits else '无'} | 检索: {display_ids}\n")
        detail_lines.append("\n")

    # 构建 Markdown
    lines = []
    lines.append("# RAG 检索评估报告\n")
    lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"**测试查询数**: {len(details)}\n")
    lines.append("\n---\n\n## 整体指标\n")

    header_cols = ["Method"] + [f"Recall@{k}" for k in ks] + [f"Hit Rate@{k}" for k in ks] + ["MRR"]
    lines.append("| " + " | ".join(header_cols) + " |\n")
    lines.append("| " + " | ".join(["---"] * len(header_cols)) + " |\n")

    for method in methods_order:
        if method not in summary:
            continue
        r = summary[method]
        cols = [labels[method]]
        for k in ks:
            cols.append(f"{r.get(f'recall@{k}', 0):.4f}")
        for k in ks:
            cols.append(f"{r.get(f'hit_rate@{k}', 0):.4f}")
        cols.append(f"{r.get('mrr', 0):.4f}")
        lines.append("| " + " | ".join(cols) + " |\n")

    lines.append("\n---\n\n## 逐查询详情\n")
    lines.extend(detail_lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    print(f"\n报告已保存到 {output_path}")
    return output_path
