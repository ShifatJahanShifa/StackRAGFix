from langchain_ollama import ChatOllama, OllamaEmbeddings


class Model:
    def __init__(self):
        self.ollamaEmbeddings = OllamaEmbeddings(model="mxbai-embed-large:latest")
        self.ollamaChat = ChatOllama(model="llama3:8b", temperature=0)
