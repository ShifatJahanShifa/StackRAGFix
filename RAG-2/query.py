from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma

from constants import COLLECTION_NAME, PERSISTENT_DATABASE_DIRECTORY
from model import Model

model = Model()
embeddingModel = model.ollamaEmbeddings
chatModel = model.ollamaChat

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""


def main():
    query_text = input("ask your question: ")
    query_rag(query_text)


def query_rag(query_text: str):
    vectorStore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddingModel,
        persist_directory=PERSISTENT_DATABASE_DIRECTORY,
    )

    results = vectorStore.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)
    print(f"debug: {prompt}")

    response_text = chatModel.invoke(prompt)

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text.content}\nSources: {sources}"
    print(formatted_response)


if __name__ == "__main__":
    main()
