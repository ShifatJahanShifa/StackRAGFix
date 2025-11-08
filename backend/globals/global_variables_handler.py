import globals.global_variables
from typing import List, Dict

def set_question(question: str):
    globals.global_variables.global_question = question

def get_question() -> str: 
    return globals.global_variables.global_question


def set_unanswered_question_list(unanswered_question_list: List):
    globals.global_variables.global_unanswered_question_list.append(unanswered_question_list)

def get_unanswered_question_list() -> List: 
    return globals.global_variables.global_unanswered_question_list

def clear_unanswered_question_lists():
    globals.global_variables.global_unanswered_question_list.clear()


def set_user_query(query: str):
    globals.global_variables.user_query = query

def get_user_query() -> str:
    return globals.global_variables.user_query


def set_evidence(evidence: str):
    globals.global_variables.global_evidence=evidence

def get_evidence() -> str: 
    return globals.global_variables.global_evidence


def set_extracted_keywords(keywords:  Dict):
    globals.global_variables.global_question_extracted_keywords_dict = keywords

def get_extracted_keywords() -> Dict:
    return globals.global_variables.global_question_extracted_keywords_dict


def set_generated_answer(answers: str):
    globals.global_variables.global_generated_answer = answers

def get_generated_answer() -> str:
    return globals.global_variables.global_generated_answer


def reset_all_globals():
    globals.global_variables.global_evidence = ""
    globals.global_variables.user_query = ""
    globals.global_variables.global_unanswered_question_list = []
    globals.global_variables.global_question_extracted_keywords_dict = {}
    globals.global_variables.global_generated_answer = ""
    globals.global_variables.global_question = ""