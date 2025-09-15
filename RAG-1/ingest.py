from uuid import uuid4

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from model import Model
from constants import DATA_FOLDER, CHUNK_SIZE, CHUNK_OVERLAP, CHECK_INTERVAL

model = Model()
embeddingModel=model.ollamaEmbeddings
chatModel=model.ollamaChat

#  chroma vector store
vectorStore=Chroma(
    collection_name="documents",
    embedding_function=embeddingModel,
    persist_directory='/db/chromaLangchainDB'
)


# ingest a file 
def ingestFile(filePath):
    # skip a non-pdf file
    if not filePath.lower().endswith('.pdf'):
        print(f"skipping a non-pdf file: {filePath}")
        return 

    print(f"Starting to ingest a pdf file: {filePath}")
    loader = PyPDFLoader(file_path=filePath)
    loadedDocuments = loader.load()
    print(f"debug: {loadedDocuments}")
    textSplitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separators=['\n',' ', '']
    )

    documents = textSplitter.split_documents(loadedDocuments)
    
