import os

import jieba
import tantivy


class BM25Searcher:
    """基于 Tantivy 的 BM25 关键词检索器，使用 jieba 中文分词。

    注：tantivy 标准 Python 发行版未内置 jieba 分词器，
    因此通过 jieba 库在 Python 层预先对文本进行分词，
    再交由 tantivy default 分词器做 whitespace tokenization。
    """

    def __init__(self, index_path: str):
        self.index_path = index_path
        if os.path.exists(index_path) and os.listdir(index_path):
            self.index = tantivy.Index.open(index_path)
        else:
            schema_builder = tantivy.SchemaBuilder()
            schema_builder.add_text_field("chunk_id", stored=True, tokenizer_name="raw")
            schema_builder.add_text_field("content", stored=True, tokenizer_name="default")
            self.schema = schema_builder.build()
            os.makedirs(index_path, exist_ok=True)
            self.index = tantivy.Index(self.schema, path=index_path)
        self.searcher = None
        self._writer = None

    @staticmethod
    def _segment(text: str) -> str:
        """使用 jieba 对文本分词，以空格连接。"""
        return " ".join(jieba.cut(text))

    def add_documents(self, chunks: list[dict]) -> int:
        """逐条写入文档片段。

        Args:
            chunks: [{"chunk_id": "chunk_0", "content": "..."}, ...]

        Returns:
            写入的文档数
        """
        writer = self.index.writer()
        for chunk in chunks:
            writer.add_document(tantivy.Document(
                chunk_id=chunk["chunk_id"],
                content=self._segment(chunk["content"]),
            ))
        writer.commit()
        writer.wait_merging_threads()
        self._reload()
        return len(chunks)

    def search(self, query: str, k: int = 10) -> list[tuple[str, float]]:
        """BM25 检索，返回 [(chunk_id, score), ...]"""
        self._reload()
        searcher = self.index.searcher()
        query_parsed = self.index.parse_query(self._segment(query), ["content"])
        results = searcher.search(query_parsed, limit=k)
        return [
            (searcher.doc(r[1])["chunk_id"][0], r[0])
            for r in results.hits
        ]

    def _reload(self):
        self.index.reload()
        self.searcher = self.index.searcher()

    def count(self) -> int:
        self._reload()
        return self.searcher.num_docs
