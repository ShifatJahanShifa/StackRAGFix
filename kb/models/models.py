import os

from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from langchain_ollama import ChatOllama, OllamaEmbeddings

from constants.models import (
    MISTRAL_CHAT_MODEL,
    MISTRAL_EMBEDDING_MODEL,
    OLLAMA_CHAT_MODEL,
    OLLAMA_EMBEDDING_MODEL,
)
from constants.temperatures import POINT_NINE_TEMPERATURE, ZERO_TEMPERATURE

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "your_api_key")


class OllamaModel:
    def __init__(self):
        self.ollama_embeddings = OllamaEmbeddings(model=OLLAMA_EMBEDDING_MODEL)
        self.ollama_chat = ChatOllama(
            model=OLLAMA_CHAT_MODEL, temperature=POINT_NINE_TEMPERATURE
        )


class MistralModel:
    def __init__(self):
        self.mistral_embeddings = MistralAIEmbeddings(
            model=MISTRAL_EMBEDDING_MODEL, api_key=MISTRAL_API_KEY
        )
        self.mistral_chat = ChatMistralAI(
            model=MISTRAL_CHAT_MODEL,
            api_key=MISTRAL_API_KEY,
            temperature=ZERO_TEMPERATURE,
        )
