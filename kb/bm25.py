import pickle

import chromadb
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents.base import Document

from constants.collections import JAVASCRIPT_QA_COLLECTION, PYTHON_QA_COLLECTION
from constants.files import PICKLE_PATH


def build_and_save_bm25(collection_name):
    client = chromadb.HttpClient(host="localhost", port=9000, ssl=False)

    # Load full Chroma collection
    print("Loading Chroma collection...")
    raw_collection = client.get_or_create_collection(name=collection_name)
    results = raw_collection.get(include=["documents", "metadatas"])

    texts = results["documents"]
    metadatas = results["metadatas"]

    all_docs = [
        Document(page_content=texts[i], metadata=metadatas[i])
        for i in range(len(texts))
    ]

    print(f"Total docs: {len(all_docs)}")

    # Filter only questions for BM25
    question_docs = [d for d in all_docs if d.metadata.get("type") == "question"]

    # Create BM25 retriever
    bm25_retriever = BM25Retriever.from_documents(question_docs)
    bm25_retriever.k = 5

    # Save to pickle
    with open(PICKLE_PATH, "wb") as f:
        pickle.dump(bm25_retriever, f)

    print(f"BM25 retriever saved to {PICKLE_PATH}")


build_and_save_bm25(PYTHON_QA_COLLECTION)
