# llm
from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3:8b")

response = llm.invoke("what is the capital of france?")
print(response) 

# chat model
from langchain_ollama import ChatOllama

chatmodel = ChatOllama(model="llama3:8b")
response = chatmodel.invoke("What is the capital of france?")
print(response.content)

# embeddings model
from langchain_ollama import OllamaEmbeddings

embeddingsModel = OllamaEmbeddings(model="llama3:8b")
embeddings = embeddingsModel.embed_query("what is the time now?")
print(embeddings[:5])