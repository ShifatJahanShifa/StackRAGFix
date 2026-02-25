import json

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from models.model_instances import mistral_chat_model
from prompts.codebase_summary_prompt import CODEBASE_SUMMARY_PROMPT

load_dotenv()


async def generate_codebase_summary(codebase: str):
    prompt = ChatPromptTemplate.from_template(CODEBASE_SUMMARY_PROMPT)
    chain = prompt | mistral_chat_model | StrOutputParser()
    response = await chain.ainvoke(
        {
            "codebase": codebase,
        }
    )
    return response
