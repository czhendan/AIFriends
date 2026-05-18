import gc
import shutil
import tempfile
from contextlib import contextmanager

from web.documents.utils.bm25_search import BM25Searcher


@contextmanager
def _temp_bm25_searcher():
    tmpdir = tempfile.mkdtemp()
    searcher = None
    try:
        searcher = BM25Searcher(tmpdir)
        yield searcher
    finally:
        del searcher
        gc.collect()
        shutil.rmtree(tmpdir, ignore_errors=True)


def test_bm25_searcher_creates_index_on_new_path():
    """BM25Searcher creates a new index when path is empty."""
    with _temp_bm25_searcher() as searcher:
        assert searcher.count() == 0


def test_bm25_add_and_search():
    """Add documents and retrieve them via BM25 search."""
    with _temp_bm25_searcher() as searcher:
        searcher.add_documents([
            {"chunk_id": "chunk_0", "content": "Python是一种编程语言"},
            {"chunk_id": "chunk_1", "content": "Java也是一种编程语言"},
            {"chunk_id": "chunk_2", "content": "今天天气真好"},
        ])
        assert searcher.count() == 3

        results = searcher.search("Python编程", k=2)
        assert len(results) >= 1
        assert results[0][0] == "chunk_0"


def test_bm25_search_with_content():
    """search_with_content returns (chunk_id, content) tuples."""
    with _temp_bm25_searcher() as searcher:
        searcher.add_documents([
            {"chunk_id": "c1", "content": "机器学习是人工智能的一个分支"},
        ])
        results = searcher.search_with_content("机器学习", k=5)
        assert len(results) == 1
        chunk_id, content = results[0]
        assert chunk_id == "c1"
        assert "机器" in content
        assert "学习" in content


def test_bm25_empty_query_returns_empty():
    """An empty or unparseable query returns an empty list."""
    with _temp_bm25_searcher() as searcher:
        searcher.add_documents([
            {"chunk_id": "c1", "content": "测试内容"},
        ])
        results = searcher.search("", k=5)
        assert results == []


def test_bm25_segment_chinese():
    """The _segment method tokenizes Chinese text with jieba."""
    tokens = BM25Searcher._segment("你好世界")
    assert " " in tokens
    assert len(tokens) >= 2
