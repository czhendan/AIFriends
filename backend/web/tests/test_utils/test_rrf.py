from web.documents.utils.hybrid_search import rrf_fusion


def test_rrf_single_list():
    """RRF with a single list preserves the ranking order."""
    ranked = [("a", 0.9), ("b", 0.7), ("c", 0.5)]
    result = rrf_fusion([ranked], k=60)
    assert [doc_id for doc_id, _ in result] == ["a", "b", "c"]


def test_rrf_two_lists():
    """RRF with two overlapping lists fuses scores correctly."""
    list1 = [("b", 0.9), ("a", 0.7)]
    list2 = [("b", 0.8), ("a", 0.3), ("c", 0.1)]
    result = rrf_fusion([list1, list2], k=60)
    ids = [doc_id for doc_id, _ in result]
    # b appears high in both, should rank at or near top
    assert ids[0] == "b"
    assert set(ids) == {"a", "b", "c"}


def test_rrf_empty_list():
    """RRF with an empty list is handled gracefully."""
    result = rrf_fusion([], k=60)
    assert result == []


def test_rrf_some_empty_sublists():
    """RRF with some empty sublists still works for non-empty ones."""
    result = rrf_fusion([[], [("x", 1.0)], []], k=60)
    assert result == [("x", 1 / (60 + 1))]


def test_rrf_score_values():
    """RRF scores are computed as sum of 1/(k + rank), rank 1-indexed."""
    ranked = [("doc1", 0.99), ("doc2", 0.5)]
    result = rrf_fusion([ranked], k=60)
    expected_doc1 = 1.0 / (60 + 1)
    expected_doc2 = 1.0 / (60 + 2)
    assert result[0] == ("doc1", expected_doc1)
    assert result[1] == ("doc2", expected_doc2)


def test_rrf_different_k():
    """RRF with k=10 gives different scores than k=60."""
    ranked = [("a", 0.9)]
    result = rrf_fusion([ranked], k=10)
    assert result[0][1] == 1.0 / (10 + 1)
