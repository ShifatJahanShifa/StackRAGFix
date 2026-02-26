import json

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from constants.collections import JAVASCRIPT_QA_COLLECTION, PYTHON_QA_COLLECTION
from models.model_instances import mistral_chat_model
from prompts.bug_fixing_prompt import BUG_FIXING_PROMPT
from src.keyword_extractor import extract_keywords
from src.vector_store_retriever import retrieve

load_dotenv()


async def fix_bug(
    question: str,
    language: str,
    history: list[dict[str, str]],
    code: str,
    currentFileName: str,
    currentFileContent: str,
    selectedFilesContent: str,
):
    """Main entry point"""
    # === STEP 1: Extract keywords ===
    extracted_keywords = await extract_keywords(question)

    # === STEP 2: Retrieve Stack Overflow data ===
    print("\nRetrieve first============\n")
    retrieve_docs = None
    if language == "python":
        retrieve_docs = retrieve(PYTHON_QA_COLLECTION, extracted_keywords, language)
    else:
        retrieve_docs = retrieve(JAVASCRIPT_QA_COLLECTION, extracted_keywords, language)

    # === STEP 3: Generate final answer ===
    print(f"\n=== Sending {retrieve_docs} to Mistral Model ===\n")
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a part of RAG architecture that specializes in fixing bugs according to user queries using Stack Overflow.",
            ),
            ("user", BUG_FIXING_PROMPT),
        ]
    )

    answer_chain = answer_prompt | mistral_chat_model | StrOutputParser()
    response = await answer_chain.ainvoke(
        {
            "question": question,
            "evidence": json.dumps(retrieve_docs, ensure_ascii=False, indent=2),
            "history": history,
            "code": code,
            "currentFileName": currentFileName,
            "currentFileContent": currentFileContent,
            "selectedFilesContent": selectedFilesContent,
        }
    )

    print(f"\n=== Final Response ===\n{response}")
    return response
