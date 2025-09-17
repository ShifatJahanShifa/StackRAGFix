import os

import streamlit as st
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_chroma import Chroma
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool

from constants import COLLECTION_NAME
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


# pulling prompt from hub
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
    retrieved_docs = vectorStore.similarity_search(query, k=2)

    serialized = ""

    for doc in retrieved_docs:
        serialized += (
            f"Source: {doc.metadata['source']}\nContent: {doc.page_content}\n\n"
        )

    return serialized


tools = [retrieve]

agent = create_tool_calling_agent(chatModel, tools, prompt)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


st.set_page_config(page_title="Agentic RAG Chatbot", page_icon="🦜")
st.title("🦜 Agentic RAG Chatbot")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)


user_question = st.chat_input("How are you?")

if user_question:
    with st.chat_message("user"):
        st.markdown(user_question)

        st.session_state.messages.append(HumanMessage(user_question))

    result = agent_executor.invoke(
        {"input": user_question, "chat_history": st.session_state.messages}
    )

    ai_message = result["output"]

    with st.chat_message("assistant"):
        st.markdown(ai_message)

        st.session_state.messages.append(AIMessage(ai_message))
