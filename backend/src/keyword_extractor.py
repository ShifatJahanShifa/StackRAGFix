from typing import List

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from models.model_instances import mistral_chat_model
from prompts.keyword_extractor_prompt import KEYWORD_EXTRACTOR_PROMPT
from utils.keyword_cleaner import clean_keyword, separate_keyword

load_dotenv()


async def extract_keywords(question: str) -> List[str]:
    """
    A function to extract keywords from the given question.
    :param question: A question in string
    :return: A list of keywords for the provided question
    """

    keyword_extractor_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an intelligent tool which retrieves essential keywords from a given user query.",
            ),
            ("user", KEYWORD_EXTRACTOR_PROMPT),
        ]
    )

    keyword_chain = keyword_extractor_prompt | mistral_chat_model | StrOutputParser()
    extracted_keywords = await keyword_chain.ainvoke({"question": question})

    print("\n=== Extracted keywords ===")
    print(extracted_keywords)

    return extracted_keywords

    # extracted_keyword_list = clean_keyword(extracted_keyword_list=extracted_keyword_list)
    # print(f"debug: {extracted_keyword_list}")

    # extracted_keyword_list = separate_keyword(extracted_keyword_list)
    # extracted_keyword_list = list(set(extracted_keyword_list))
    # print(f"see the keywords: {extracted_keyword_list}")
    # return extracted_keyword_list
