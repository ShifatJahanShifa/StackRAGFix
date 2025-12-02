import pickle

from langchain_chroma import Chroma

# from langchain_core.documents.base import Document
from constants.file_paths import PERSISTENT_DIRECTORY, PICKLE_PATH
from constants.weights import BM25_RETRIEVER_WEIGHT, VECTOR_RETRIEVER_WEIGHT
from models.model_instances import mistral_embedding_model
from src.custom_ensemble_retriever import CustomEnsembleRetriever


def retrieve(collection_db_name, query):
    try:
        # Connect to existing ChromaDB collection
        print("🔗 Connecting to ChromaDB for retrieval...")
        vector_store = Chroma(
            collection_name=collection_db_name,
            embedding_function=mistral_embedding_model,
            persist_directory=PERSISTENT_DIRECTORY,  # folder on disk
        )

        print("checkkk")

        with open(PICKLE_PATH, "rb") as f:
            bm25_retriever = pickle.load(f)
        print("✅ Loaded BM25 retriever from pickle.")

        # ✅ Create vector retriever (no full doc fetch)
        vector_retriever = vector_store.as_retriever(
            search_kwargs={"k": 5, "filter": {"type": "question"}}
        )

        # Combine both retrievers with weights
        ensemble_retriever = CustomEnsembleRetriever(
            retrievers=[bm25_retriever, vector_retriever],
            weights=[BM25_RETRIEVER_WEIGHT, VECTOR_RETRIEVER_WEIGHT],
        )

        questions = ensemble_retriever.get_relevant_documents(query)
        print(f"✅ Retrieved {len(questions)} questions")
        print(f"questions: {questions}")
        so_discussions = []
        # Attach answers
        for question in questions:
            q_id = question.metadata.get("question_id")
            answer_results = vector_store._collection.get(
                where={"$and": [{"type": "answer"}, {"question_id": q_id}]},
                include=["documents", "metadatas"],
            )

            print(f"debug: {answer_results}")

            so_discussions.append(
                {
                    "question": question.page_content,
                    "questionLink": question.metadata.get("link"),
                    "answers": answer_results["documents"],
                }
            )

        return so_discussions

    except Exception as e:
        print("❌ Error during retrieval:", str(e))
        return []
