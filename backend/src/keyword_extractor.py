import ast
import asyncio
import json
import src.config
from src.llm_chain import question_complexity_checker, question_divider, keyword_extractor
from utils.event_loop import get_or_create_eventloop
# global lgbe...
from utils.keyword_cleaner import clean_keyword, separate_keyword

from globals.global_variables_handler import (
    get_evidence,
    get_extracted_keywords,
    get_generated_answer,
    get_question,
    get_unanswered_question_list,
    get_user_query,
    set_generated_answer,
    set_evidence,
    set_extracted_keywords,
    set_question,
    set_unanswered_question_list,
    set_user_query,
    reset_all_globals
)

from typing import List

async def async_generate_keywords(question_list: List[str]) -> List[str]:
    """
    A function that asynchronously generates keywords based on the provided list of question
    :param question_list: A list of questions
    :return: A coroutine object, which, when run, returns a list of keywords for each of the provided questions
    """

    tasks = [keyword_extractor.arun(question) for question in question_list]
    results = await asyncio.gather(*tasks)
    return results

def generate_keywords(question_list: str) -> List[str]:
    """
    A wrapper function to execute keyword generation (async_generate_keywords) based on the provided list of questions
    :param question_list: A list of questions
    :return: A list of keywords for each of the provided questions
    """
    # global user_query
    # user_query = question_list 
    set_user_query(query=question_list)

    # global global_generated_answer
    # global_generated_answer = ""
    set_generated_answer("")
    question_complexity = question_complexity_checker.run(question_list)

    if question_complexity.upper() == "TRUE":
        question_list = question_divider.run(question_list)

    print(f"debug: {question_list}")
    loop = get_or_create_eventloop()

    question_list = ast.literal_eval(question_list)

    extracted_keyword_list = loop.run_until_complete(async_generate_keywords(question_list))

    print(f"debug: {extracted_keyword_list}")
    extracted_keyword_list = clean_keyword(extracted_keyword_list=extracted_keyword_list)
    print(f"debug: {extracted_keyword_list}")


    # extracted_keyword_list = sum([json.loads(extracted_keyword) for extracted_keyword in extracted_keyword_list], [])
    extracted_keyword_list = separate_keyword(extracted_keyword_list)
    extracted_keyword_list = list(set(extracted_keyword_list))
    print(f"see the keywords: {extracted_keyword_list}")
    return extracted_keyword_list