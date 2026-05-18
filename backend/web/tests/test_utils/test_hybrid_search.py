import os

import pytest

from web.documents.utils.hybrid_search import (
    hybrid_search,
    vector_search_only,
    bm25_search_only,
    LANCE_URI,
    TANTIVY_PATH,
)


def _has_lancedb_data():
    return os.path.isdir(LANCE_URI)


def _has_tantivy_data():
    return os.path.isdir(TANTIVY_PATH) and os.listdir(TANTIVY_PATH)


@pytest.mark.skipif(not _has_lancedb_data(), reason="LanceDB index not found")
def test_vector_search_only_returns_tuples():
    results = vector_search_only("测试", k=3)
    assert isinstance(results, list)
    if results:
        assert len(results[0]) == 2


@pytest.mark.skipif(not _has_tantivy_data(), reason="Tantivy index not found")
def test_bm25_search_only_returns_tuples():
    results = bm25_search_only("测试", k=3)
    assert isinstance(results, list)
    if results:
        assert len(results[0]) == 2


@pytest.mark.skipif(
    not (_has_lancedb_data() and _has_tantivy_data()),
    reason="Both LanceDB and Tantivy indexes required",
)
def test_hybrid_search_returns_list_of_dicts():
    results = hybrid_search("Python编程", k_vector=5, k_bm25=5, final_k=3)
    assert isinstance(results, list)
    assert len(results) <= 3
    if results:
        assert "chunk_id" in results[0]
        assert "content" in results[0]
        assert "score" in results[0]


@pytest.mark.skipif(
    not (_has_lancedb_data() and _has_tantivy_data()),
    reason="Both LanceDB and Tantivy indexes required",
)
def test_hybrid_search_respects_final_k():
    results = hybrid_search("测试", k_vector=10, k_bm25=10, final_k=2)
    assert len(results) <= 2


def test_module_imports():
    """Verify all public functions are importable."""
    assert callable(hybrid_search)
    assert callable(vector_search_only)
    assert callable(bm25_search_only)
