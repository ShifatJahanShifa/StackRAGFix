import pickle

import chromadb
from langchain_chroma import Chroma

from constants.file_paths import PERSISTENT_DIRECTORY
from constants.weights import BM25_RETRIEVER_WEIGHT, VECTOR_RETRIEVER_WEIGHT
from models.model_instances import mistral_embedding_model
from src.custom_ensemble_retriever import CustomEnsembleRetriever
from utils.logger import logger
from utils.pickle_loader import JS_BM25_RETRIEVER, PY_BM25_RETRIEVER


def retrieve(collection_db_name, query, language):
    try:
        # Connect to existing ChromaDB collection
        # need to change it when deploying it....
        logger.info("🔗 Connecting to ChromaDB for retrieval...")
        remote_client = chromadb.HttpClient(
            host="https://shifa1301-stackrag.hf.space", ssl=True
        )
        vector_store = Chroma(
            collection_name=collection_db_name,
            embedding_function=mistral_embedding_model,
            persist_directory=PERSISTENT_DIRECTORY,  # folder on disk
            # client=remote_client
        )

        logger.debug("checkkk")

        bm25_retriever = None
        if language == "python":
            bm25_retriever = PY_BM25_RETRIEVER
        else:
            bm25_retriever = JS_BM25_RETRIEVER

        # Create vector retriever (no full doc fetch)
        vector_retriever = vector_store.as_retriever(
            search_kwargs={"k": 5, "filter": {"type": "question"}}
        )

        # Combine both retrievers with weights
        ensemble_retriever = CustomEnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[BM25_RETRIEVER_WEIGHT, VECTOR_RETRIEVER_WEIGHT],
        )

        questions = ensemble_retriever.get_relevant_documents(query)
        print(f" Retrieved {len(questions)} questions")
        # print(f"questions: {questions}")
        so_discussions = []
        # Attach answers
        for question in questions:
            q_id = question.metadata.get("question_id")
            answer_results = vector_store._collection.get(
                where={"$and": [{"type": "answer"}, {"question_id": q_id}]},
                include=["documents", "metadatas"],
            )

            # print(f"debug: {answer_results}")

            so_discussions.append(
                {
                    "question": question.page_content,
                    "questionLink": question.metadata.get("link"),
                    "answers": answer_results["documents"],
                }
            )

        return so_discussions

    except Exception as e:
        print("Error during retrieval:", str(e))
        return []
