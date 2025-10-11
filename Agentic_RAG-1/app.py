import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage

from constants import COLLECTION_NAME
from model import Model

load_dotenv()

app = FastAPI(title="RAG Backend", version="1.0.0")

model = Model()
embedding_model = model.ollamaEmbeddings
chat_model = model.ollamaChat

vectorStore = Chroma(
    collection_name=COLLECTION_NAME,
    embedding_function=embedding_model,
    persist_directory="./db/chromaLangchainDB",
)

prompt = PromptTemplate.from_template(
    """                                
    You are a helpful assistant. You will be provided with a query and a chat history.
    Your task is to retrieve relevant information from the vector store and provide a response.
    For this you use the tool 'retrieve' to get the relevant information.
                                        
    The query is as follows:                    
    {input}

    The chat history is as follows:
    {chat_history}

    Please provide a concise and informative response based on the retrieved information.
    If you don't know the answer, say "I don't know" (and don't provide a source).
                                        
    You can use the scratchpad to store any intermediate results or notes.
    The scratchpad is as follows:
    {agent_scratchpad}

    For every piece of information you provide, also provide the source.

    Return text as follows:

    <Answer to the question>
    Source: source_url
    """
    )

@tool
def retrieve(query: str):
    """Retrieve information related to a query."""
    docs = vectorStore.similarity_search(query, k=2)
    return "\n\n".join(
        f"Source: {doc.metadata['source']}\nContent: {doc.page_content}"
        for doc in docs
    )

tools = [retrieve]
agent = create_tool_calling_agent(chat_model, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ==== API Models ====
class ChatRequest(BaseModel):
    query: str
    history: list[dict] = []  # [{"role": "user"/"assistant", "content": "..."}]

class ChatResponse(BaseModel):
    response: str

# ==== API Routes ====
@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        chat_history = []
        for msg in req.history:
            if msg["role"] == "user":
                chat_history.append(HumanMessage(msg["content"]))
            else:
                chat_history.append(AIMessage(msg["content"]))

        result = agent_executor.invoke(
            {"input": req.query, "chat_history": chat_history}
        )

        return ChatResponse(response=result["output"])
    except Exception as e:
        print("errorrrr", e)
        raise HTTPException(status_code=500, detail=str(e))
