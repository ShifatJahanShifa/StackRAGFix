import json

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI

from constants.collections import QA_COLLECTION
from models.model_instances import mistral_chat_model
from prompts.chat_prompt import CHAT_PROMPT
from src.keyword_extractor import extract_keywords
from src.vector_store_retriever import retrieve

load_dotenv()


async def refactor_code(question: str):
    """Main entry point"""
    # === STEP 1: Extract keywords ===
    extracted_keywords = extract_keywords(question)

    # === STEP 2: Retrieve Stack Overflow data ===
    print("\nRetrieve first============\n")
    retrieve_docs = retrieve(QA_COLLECTION, extracted_keywords)

    # === STEP 3: Generate final answer ===
    print(f"\n=== Sending {retrieve_docs} to Mistral Model ===\n")
    answer_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a part of RAG architecture that specializes in generating answers to user queries using Stack Overflow.",
            ),
            ("user", CHAT_PROMPT),
        ]
    )

    answer_chain = answer_prompt | mistral_chat_model | StrOutputParser()
    response = await answer_chain.ainvoke(
        {
            "question": question,
            "evidence": json.dumps(retrieve_docs, ensure_ascii=False, indent=2),
        }
    )

    print(f"\n=== Final Response ===\n{response}")
    return response


# if __name__ == "__main__":
#     asyncio.run(main("What does the &quot;yield&quot; keyword do in Python?"))
