import json
import os
from uuid import uuid4

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import CHUNK_OVERLAP, CHUNK_SIZE, COLLECTION_NAME
from model import Model

load_dotenv()

model = Model()
embeddingModel = model.ollamaEmbeddings
chatModel = model.ollamaChat

#  chroma vector store . i can move it to a separate file  as it is being reused.
vectorStore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embeddingModel,
    persist_directory="./db/chromaLangchainDB",
)

textSplitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""],
)


def processJsonLines(filePath):
    """Process each JSON line and extract relevant information."""
    extracted = []

    with open(filePath, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            extracted.append(obj)

    return extracted


fileContent = processJsonLines(os.getenv("DATASET_STORAGE_FOLDER") + "data.txt")

for line in fileContent:
    print(line["url"])

    documents = []
    documents = textSplitter.create_documents(
        [line["raw_text"]], metadatas=[{"source": line["url"], "title": line["title"]}]
    )

    uuids = [str(uuid4()) for _ in range(len(documents))]

    vectorStore.add_documents(documents=documents, ids=uuids)
