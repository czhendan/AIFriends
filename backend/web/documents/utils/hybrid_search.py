"""混合检索模块：向量检索 + BM25 关键词检索 + RRF 分数融合。

Public functions:
    rrf_fusion(ranked_lists, k=60)
    hybrid_search(query, ...)
    vector_search_only(query, k=5)
    bm25_search_only(query, k=5)
"""

from pathlib import Path

import lancedb

from web.documents.utils.bm25_search import BM25Searcher
from web.documents.utils.custom_embeddings import CustomEmbeddings

# ── 路径计算 ──────────────────────────────────────────────────────
# hybrid_search.py 位于 backend/web/documents/utils/
# 4 级目录向上 = backend/
_FILE_DIR = Path(__file__).resolve().parent
BASE_DIR = _FILE_DIR.parent.parent.parent  # backend/

LANCE_URI = str(BASE_DIR / "web" / "documents" / "lancedb_storage")
TANTIVY_PATH = str(BASE_DIR / "web" / "documents" / "tantivy_index")
TABLE_NAME = "my_knowledge_base"


# ── 内部 helpers ──────────────────────────────────────────────────


def _vector_search_with_scores(query, k=10):
    """使用原始 LanceDB 表 API 进行向量检索，保证能获取 id、text 和距离分数。

    LanceDB LangChain 包装器在 results_to_docs 中丢弃了 id 列，
    因此直接使用底层 table API 以正确获取每个 chunk 的 id。

    Returns:
        [(chunk_id, content, l2_distance), ...] 按 L2 距离升序排列（距离越小越相似）。
    """
    db = lancedb.connect(LANCE_URI)
    table = db.open_table(TABLE_NAME)
    embeddings = CustomEmbeddings()
    query_vec = embeddings.embed_query(query)
    results = table.search(query_vec).limit(k).to_arrow()
    return [
        (results["id"][i].as_py(),
         results["text"][i].as_py(),
         results["_distance"][i].as_py())
        for i in range(len(results))
    ]


def _get_bm25_searcher():
    """创建并返回 BM25Searcher 实例（已 reload）。"""
    bm25 = BM25Searcher(TANTIVY_PATH)
    bm25._reload()
    return bm25


def _bm25_search_with_content(query, k=10):
    """BM25 检索，同时返回 content，避免二次查询。

    Returns:
        [(chunk_id, content, score), ...]
    """
    bm25 = _get_bm25_searcher()
    searcher = bm25.searcher

    query_parsed = bm25.index.parse_query(bm25._segment(query), ["content"])
    if query_parsed is None:
        return []
    results = searcher.search(query_parsed, limit=k)
    return [
        (searcher.doc(r[1])["chunk_id"][0],
         searcher.doc(r[1])["content"][0],
         r[0])
        for r in results.hits
    ]


# ── RRF ───────────────────────────────────────────────────────────


def rrf_fusion(ranked_lists, k=60):
    """RRF 融合多个排序列表。

    公式: score(d) = Σ 1 / (k + rank_i(d))
    其中 rank 是 1-indexed（rank=1 表示最相关，即列表中的第一个元素）。

    Args:
        ranked_lists: list of list of (doc_id, any_score)
                      — 每个子列表按相关性降序排列，any_score 在融合中被忽略，
                        仅使用文档在列表中的排序位置。
        k: RRF 常数，默认 60。

    Returns:
        [(doc_id, score), ...] 按融合后分数降序排列。
    """
    scores = {}
    for ranked_list in ranked_lists:
        for rank, (doc_id, _) in enumerate(ranked_list, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ── 混合检索 ──────────────────────────────────────────────────────


def hybrid_search(query, k_vector=10, k_bm25=10, final_k=5, k_rrf=60):
    """混合检索：向量检索 + BM25 关键词检索 + RRF 分数融合。

    Args:
        query: 查询文本。
        k_vector: 向量检索返回的候选条数。
        k_bm25: BM25 检索返回的候选条数。
        final_k: 最终返回的融合结果条数。
        k_rrf: RRF 参数。

    Returns:
        [{"chunk_id": ..., "content": ..., "score": ...}, ...]
    """
    # ── 1. 向量检索 ──
    vec_results = _vector_search_with_scores(query, k=k_vector)
    # _vector_search_with_scores 返回 [(chunk_id, content, l2_distance), ...]
    # l2_distance 越小越相似，RRF 只使用排序位置（将 l2_distance 作为 score 传入排序列表）
    vector_ranked = [(chunk_id, l2_dist) for chunk_id, _, l2_dist in vec_results]
    lancedb_content_map = {chunk_id: content for chunk_id, content, _ in vec_results}

    # ── 2. BM25 检索 ──
    bm25_results = _bm25_search_with_content(query, k=k_bm25)
    bm25_ranked = [(chunk_id, score) for chunk_id, _, score in bm25_results]
    bm25_content_map = {chunk_id: content for chunk_id, content, _ in bm25_results}

    # ── 3. RRF 融合 ──
    fused = rrf_fusion([vector_ranked, bm25_ranked], k=k_rrf)

    # ── 4. 组装最终结果 ──
    # content 优先从 BM25 结果中取（因为 BM25 已经带了 content），
    # 若 BM25 中没有则从 LanceDB 结果中取。
    results = []
    for doc_id, score in fused[:final_k]:
        content = bm25_content_map.get(doc_id)
        if content is None:
            content = lancedb_content_map.get(doc_id, "")
        results.append({
            "chunk_id": doc_id,
            "content": content,
            "score": score,
        })

    return results


# ── 单一检索（用于评估对比） ──────────────────────────────────────


def vector_search_only(query, k=5):
    """仅使用向量检索（用于评估对比）。

    Returns:
        [(chunk_id, content), ...]
    """
    results = _vector_search_with_scores(query, k=k)
    return [(chunk_id, content) for chunk_id, content, _ in results]


def bm25_search_only(query, k=5):
    """仅使用 BM25 关键词检索（用于评估对比）。

    Returns:
        [(chunk_id, content), ...]
    """
    results = _bm25_search_with_content(query, k=k)
    return [(chunk_id, content) for chunk_id, content, _ in results]
