import streamlit as st
from langchain_community.document_loaders import SeleniumURLLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import CHUNK_OVERLAP, CHUNK_SIZE
from model import Model

model = Model()
embeddingModel = model.ollamaEmbeddings
chatModel = model.ollamaChat

# i am using in memory vector store for the first time
vector_store = InMemoryVectorStore(embedding=embeddingModel)

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""


def load_page(url: str):
    loader = SeleniumURLLoader(urls=[url])
    documents = loader.load()
    return documents


def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents=documents)
    return chunks


def ingestion(chunks):
    vector_store.add_documents(documents=chunks)


def retrieve(query):
    return vector_store.similarity_search(query)


def generate_answer(question, context):
    prompt = ChatPromptTemplate.from_template(template=template)
    chain = prompt | chatModel
    return chain.invoke({"question": question, "context": context})


st.title("AI Crawler")
url = st.text_input("Enter URL:")

documents = load_page(url)
chunked_documents = split_documents(documents)

ingestion(chunked_documents)

question = st.chat_input()  # universal input box

if question:
    st.chat_message("user").write(question)
    retrieve_documents = retrieve(question)
    context = "\n\n".join([doc.page_content for doc in retrieve_documents])
    answer = generate_answer(question, context)
    st.chat_message("assistant").write(answer.content)
