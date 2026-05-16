import os
import lancedb
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import LanceDB
from langchain_text_splitters import RecursiveCharacterTextSplitter

from web.documents.utils.custom_embeddings import CustomEmbeddings
from web.documents.utils.bm25_search import BM25Searcher

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def insert_documents():
    # 1. 加载并切分文档
    data_path = os.path.join(BASE_DIR, "data.txt")
    loader = TextLoader(data_path, encoding='utf-8')
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_documents(documents)
    print(f"已切分成{len(texts)}个片段")

    # 2. 生成统一的 chunk_id
    chunk_ids = [f"chunk_{i}" for i in range(len(texts))]
    metadatas = [{"id": cid} for cid in chunk_ids]
    page_contents = [doc.page_content for doc in texts]

    # 3. 写入 LanceDB（向量索引）
    embeddings = CustomEmbeddings()
    db = lancedb.connect(os.path.join(BASE_DIR, "lancedb_storage"))
    vector_db = LanceDB(
        embedding=embeddings,
        connection=db,
        table_name='my_knowledge_base',
        mode='overwrite',
    )
    vector_db.add_texts(
        texts=page_contents,
        metadatas=metadatas,
        ids=chunk_ids,
    )
    print(f"LanceDB: 已插入{len(chunk_ids)}行数据")

    # 4. 写入 Tantivy（BM25 索引）
    tantivy_path = os.path.join(BASE_DIR, "tantivy_index")
    bm25 = BM25Searcher(tantivy_path)
    chunks = [{"chunk_id": cid, "content": content} for cid, content in zip(chunk_ids, page_contents)]
    bm25.add_documents(chunks)
    print(f"Tantivy: 已插入{len(chunk_ids)}行数据")