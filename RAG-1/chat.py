from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate

from model import Model

model = Model()
embeddingModel = model.ollamaEmbeddings
chatModel = model.ollamaChat

#  chroma vector store
vectorStore = Chroma(
    collection_name="documents",
    embedding_function=embeddingModel,
    persist_directory="./db/chromaLangchainDB",
)

# prompt template
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer the user's question based on only the provided data.",
        ),
        (
            "human",
            "Answer the user question {input}. Use only the {context} to answer the question.",
        ),
    ]
)

# create retrieval chain
retrievar = vectorStore.as_retriever(kwargs={"k": 10})
documentChain = create_stuff_documents_chain(llm=chatModel, prompt=prompt)
retrievalChain = create_retrieval_chain(retrievar, documentChain)


def main():
    while True:
        query = input(
            "User (or type 'q' or 'quit' or 'exit' to end the conversation): "
        )
        if query.lower() in ["q", "quit", "exit"]:
            break

        response = retrievalChain.invoke({"input": query})
        print(f"Assistant: {response['answer']} \n\n")


if __name__ == "__main__":
    main()
