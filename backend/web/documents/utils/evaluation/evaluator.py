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


def precision_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """前 k 个结果中相关文档的占比（占检索结果）。"""
    retrieved_k = retrieved_ids[:k]
    hits = len(set(retrieved_k) & set(relevant_ids))
    return hits / k if k > 0 else 0.0


def mrr(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """Mean Reciprocal Rank：第一个相关文档排名的倒数。"""
    for i, rid in enumerate(retrieved_ids):
        if rid in relevant_ids:
            return 1.0 / (i + 1)
    return 0.0


def evaluate(queries: list[dict], ks: list[int] = None) -> dict:
    """对测试集执行三路检索评估。

    Args:
        queries: [{"id": "q001", "question": "...", "relevant_chunk_ids": [...]}, ...]
        ks: 评估的 k 值列表，默认 [3, 5, 10]

    Returns:
        {"vector": {"recall@3": ..., "mrr": ...}, "bm25": {...}, "hybrid": {...}}
    """
    if ks is None:
        ks = [3, 5, 10]

    methods: dict[str, callable] = {
        "vector": lambda q: [cid for cid, _ in vector_search_only(q, k=max(ks))],
        "bm25": lambda q: [cid for cid, _ in bm25_search_only(q, k=max(ks))],
        "hybrid": lambda q: [r["chunk_id"] for r in hybrid_search(q, k_vector=10, k_bm25=10, final_k=max(ks))],
    }

    results: dict[str, dict] = {}
    for method_name, search_fn in methods.items():
        all_recall: dict[int, list[float]] = {k: [] for k in ks}
        all_precision: dict[int, list[float]] = {k: [] for k in ks}
        all_mrr: list[float] = []

        for query_data in queries:
            question: str = query_data["question"]
            relevant: list[str] = query_data["relevant_chunk_ids"]
            retrieved_ids: list[str] = search_fn(question)

            for k in ks:
                all_recall[k].append(recall_at_k(retrieved_ids, relevant, k))
                all_precision[k].append(precision_at_k(retrieved_ids, relevant, k))
            all_mrr.append(mrr(retrieved_ids, relevant))

        method_result: dict[str, float] = {"mrr": sum(all_mrr) / len(all_mrr) if all_mrr else 0.0}
        for k in ks:
            method_result[f"recall@{k}"] = sum(all_recall[k]) / len(all_recall[k]) if all_recall[k] else 0.0
            method_result[f"precision@{k}"] = sum(all_precision[k]) / len(all_precision[k]) if all_precision[k] else 0.0
        results[method_name] = method_result

    return results


def print_report(results: dict, ks: list[int] = None):
    """打印评估对比报告。"""
    if ks is None:
        ks = [3, 5, 10]

    methods_order = ["vector", "bm25", "hybrid"]
    labels = {"vector": "Vector-only", "bm25": "BM25-only", "hybrid": "Hybrid(RRF)"}

    header_cols = ["Method"] + [f"Recall@{k}" for k in ks] + [f"Precision@{k}" for k in ks] + ["MRR"]
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
            cols.append(f"{r.get(f'precision@{k}', 0):.4f}")
        cols.append(f"{r.get('mrr', 0):.4f}")
        row = "  ".join(f"{col:<14}" for col in cols)
        print(row)
