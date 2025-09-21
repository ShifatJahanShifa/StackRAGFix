from langchain_ollama import ChatOllama, OllamaEmbeddings


class Model:
    def __init__(self):
        self.ollamaEmbeddings = OllamaEmbeddings(model="mxbai-embed-large:latest")
