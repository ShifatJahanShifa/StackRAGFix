import uuid

import pandas as pd
from langchain_core.documents import Document

from db import vector_store


class Portfolio:
    def __init__(self, file_path="resources/my_portfolio.csv"):
        self.file_path = file_path
        self.data = pd.read_csv(file_path)
        self.collection = vector_store

    def load_portfolio(self):
        count = self.collection.client.count(
            collection_name=self.collection.collection_name
        ).count
        if count == 0:
            for _, row in self.data.iterrows():
                self.collection.add_documents(
                    documents=[
                        Document(
                            page_content=row["Techstack"],
                            metadata={"links": row["Links"]},
                        )
                    ],
                    ids=[str(uuid.uuid4())],
                )

    def query_links(self, skills):
        query_str = ", ".join(skills) if isinstance(skills, list) else str(skills)
        results = self.collection.similarity_search(query=query_str, k=2)
        links = [doc.metadata.get("links") for doc in results]
        return links
