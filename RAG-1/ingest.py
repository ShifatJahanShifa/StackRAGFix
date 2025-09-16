import os
import time
from uuid import uuid4

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import CHUNK_OVERLAP, CHUNK_SIZE, DATA_FOLDER, FOLDER_CHECK_INTERVAL
from model import Model

model = Model()
embeddingModel = model.ollamaEmbeddings
chatModel = model.ollamaChat

#  chroma vector store . i can move it to a separate file  as it is being reused.
vectorStore = Chroma(
    collection_name="documents",
    embedding_function=embeddingModel,
    persist_directory="./db/chromaLangchainDB",
)


# ingest a file
def ingestFile(filePath):
    # skip a non-pdf file
    if not filePath.lower().endswith(".pdf"):
        print(f"skipping a non-pdf file: {filePath}")
        return

    print(f"Starting to ingest a pdf file: {filePath}")
    loader = PyPDFLoader(file_path=filePath)
    loadedDocuments = loader.load()
    textSplitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""],
    )

    documents = textSplitter.split_documents(loadedDocuments)
    print(f"debug {documents}")
    uuids = [str(uuid4()) for _ in range(len(documents))]
    print(f"Adding {len(documents)} to the vector store...")
    vectorStore.add_documents(documents=documents, ids=uuids)
    print(f"finish ingesting the file: {filePath}")


def mainLoop():
    while True:
        for fileName in os.listdir(DATA_FOLDER):
            if not fileName.startswith("_"):
                filePath = os.path.join(DATA_FOLDER, fileName)
                ingestFile(filePath)
                newFileName = "_" + fileName
                newFilePath = os.path.join(DATA_FOLDER, newFileName)
                os.rename(filePath, newFilePath)

        time.sleep(FOLDER_CHECK_INTERVAL)


if __name__ == "__main__":
    mainLoop()
