import os
from uuid import uuid4

from langchain.schema.document import Document
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    COLLECTION_NAME,
    DATA_FOLDER,
    PERSISTENT_DATABASE_DIRECTORY,
)
from model import Model

model = Model()
embeddingModel = model.ollamaEmbeddings
chatModel = model.ollamaChat


def load_documents():
    document_loader = PyPDFDirectoryLoader(DATA_FOLDER)
    return document_loader.load()


def split_documents(documents: list[Document]):
    textSplitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )
    return textSplitter.split_documents(documents=documents)


def add_to_database(chunks: list[Document]):
    vectorStore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddingModel,
        persist_directory=PERSISTENT_DATABASE_DIRECTORY,
    )

    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = vectorStore.get(
        include=[]
    )  # IDs are always included by default. others may be embeddings, metadatas, documents
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in vectorStore: {len(existing_ids)}")

    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        vectorStore.add_documents(new_chunks, ids=new_chunk_ids)
        # vectorStore.persist()
    else:
        print("No new documents to add")


def calculate_chunk_ids(chunks):
    """calculate chunk id = Page Source : Page Number : Chunk Index"""
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        chunk.metadata["id"] = chunk_id

    return chunks


def main():
    documents = load_documents()
    chunks = split_documents(documents)
    add_to_database(chunks)


if __name__ == "__main__":
    main()
