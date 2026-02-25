class CustomEnsembleRetriever:
    def __init__(self, retrievers, weights):
        assert len(retrievers) == len(weights), "Each retriever must have a weight."
        self.retrievers = retrievers
        self.weights = weights

    def get_relevant_documents(self, query):
        """Combine results from all retrievers based on weights."""
        all_docs = []

        # Step 1: Retrieve from each retriever
        for retriever, weight in zip(self.retrievers, self.weights):
            if hasattr(retriever, "get_relevant_documents"):
                docs = retriever.get_relevant_documents(query)
            elif hasattr(retriever, "invoke"):
                docs = retriever.invoke(query)
            else:
                raise AttributeError(
                    "Retriever must have either get_relevant_documents or invoke method."
                )

            for doc in docs:
                all_docs.append((doc, weight))

        # Step 2: Combine duplicate documents with weighted scores
        combined = {}
        for doc, weight in all_docs:
            doc_id = doc.page_content.strip()
            if doc_id not in combined:
                combined[doc_id] = {"doc": doc, "score": 0}
            combined[doc_id]["score"] += weight

        # Step 3: Sort by descending score
        sorted_docs = sorted(combined.values(), key=lambda x: x["score"], reverse=True)

        return [entry["doc"] for entry in sorted_docs]
