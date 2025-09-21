import os

from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

from constants import COLLECTION_NAME
from model import Model

load_dotenv()

client = QdrantClient(
    url=os.getenv("QDRANT_ENDPOINT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
)

if not client.collection_exists(collection_name=COLLECTION_NAME):
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE),
    )

model = Model()

vector_store = QdrantVectorStore(
    client=client, collection_name=COLLECTION_NAME, embedding=model.ollamaEmbeddings
)
