import ast
import asyncio
import json
import logging
import src.config
from src.llm_chain import evidence_checker, evidence_scorer
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import random
import os
import logging
# from backend.models.model import Model
# from langchain.vectorstores import Pinecone
from langchain_pinecone import Pinecone
# import pinecone

from rank_bm25 import BM25Okapi

from utils.event_loop import get_or_create_eventloop

from stackapi import StackAPI

from typing import Dict, List, Tuple
# from backend.models.model import Model

# global lgbe...
from globals.global_variables_handler import (
    # get_evidence,
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

from models.model_instance import chatModel, embeddingModel
load_dotenv(find_dotenv())


# model = Model()
# embeddingModel = model.ollamaEmbeddings
# chatModel = model.ollamaChat




PINECONE_STACK_RAG_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_STACK_RAG_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
PINECONE_STACK_RAG_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
SO_CLIENT_SECRET = os.getenv('SO_CLIENT_SECRET')
SO_KEY = os.getenv('SO_KEY')
SITE = StackAPI('stackoverflow', client_secret=SO_CLIENT_SECRET, key=SO_KEY)


def choose_top3_evidences(best_scores: List[int], evidence_score: int, index: int, top_scorer_indices: List[int], final_answer_list: List[str], best_answers: List[str]) -> Tuple[List[str], List[int], List[int]]:
    if evidence_score > best_scores[0] and evidence_score > best_scores[1]:
        if best_scores[0] > best_scores[1]:
            top_scorer_indices[1] = index
            best_scores[1] = evidence_score
            final_answer_list[1] = best_answers[index]
        elif best_scores[1] > best_scores[0]:
            top_scorer_indices[0] = index
            best_scores[0] = evidence_score
            final_answer_list[0] = best_answers[index]
        else:
            index_to_remove = random.choices([0, 1], k=1)[0]
            top_scorer_indices[index_to_remove] = index
            best_scores[index_to_remove] = evidence_score
            final_answer_list[index_to_remove] = best_answers[index]

    elif evidence_score > best_scores[0] and evidence_score < best_scores[1]:
        top_scorer_indices[0] = index
        best_scores[0] = evidence_score
        final_answer_list[0] = best_answers[index]

    elif evidence_score < best_scores[0] and evidence_score > best_scores[1]:
        top_scorer_indices[1] = index
        best_scores[1] = evidence_score
        final_answer_list[1] = best_answers[index]

    elif evidence_score == best_scores[0] and evidence_score == best_scores[1]:
        index_to_remove = random.choices([0, 2], k=1)
        if index_to_remove == 0 or index_to_remove == 1:
            top_scorer_indices[index_to_remove] = index
            best_scores[index_to_remove] = evidence_score
            final_answer_list[index_to_remove] = best_answers[index]

    return final_answer_list, best_scores, top_scorer_indices


async def async_score_evidence(evidence_list: List[str], question: str) -> List[str]:
    """
    A function to asynchronously score all of the retrieved evidences (answers from stack-overflow)
    :param evidence_list: A list of Stack-overflow answers retrieved from vector store
    :param question: User given question
    :return: A coroutine object, which, when run, returns a list of numbers from 1 to 5 indicating the usefulness of each answer to the given question, with higher indicating better, or "not useful" if the answer is not useful at all
    """
    logging.info("---"*100)
    for evidence in evidence_list:
        logging.info(f"CURRENT EVIDENCE: {evidence.page_content}")
        logging.info(f"QUESTION: {question}")
    score_tasks = [evidence_scorer.arun(evidence=evidence.page_content, question=question) for evidence in evidence_list]
    results = await asyncio.gather(*score_tasks)
    return results


def score_evidence(evidence_list: List[str], question: str) -> List[str]:
    """
    A wrapper function to execute evidence scoring (async_score_evidence) using the given evidence list and user question
    :param evidence_list: A list of Stack-overflow answers retrieved from vector store
    :param question: User given question
    :return: A list of numbers from 1 to 5 indicating the usefulness of each answer to the given question, with higher indicating better, or "not useful" if the answer is not useful at all
    """
    logging.info("***"*100)

    logging.info(f"QUESTION BEFORE SCORE: {question}")
    logging.info(f"EVIDENCE BEFORE SCORE: {evidence_list}")
    loop = get_or_create_eventloop()
    evidence_score_list = loop.run_until_complete(async_score_evidence(evidence_list, question))

    return evidence_score_list


def search_answer(question: str) -> List[str]:
    """
    A function to search for relevant answers for the given question in Pinecone using cosine similarity, and then choosing best matches for diversity using Maximum Marginal Relevance (MMR)
    :param question: User given question
    :return: Best answers from Vector Store
    """
    docsearch = Pinecone.from_existing_index(index_name=PINECONE_STACK_RAG_INDEX_NAME, embedding=embeddingModel)
    best_answers = docsearch.max_marginal_relevance_search(question, k=15, fetch_k=30)
    return best_answers


def gather_and_check_evidence(best_answers: List[str], question: str) -> str:
    """
    A function that uses search results from vector store to filter them out and leave the ones that are applicable for answering the question.
    :param best_answers: Best answers retrieved from vector store using MMR
    :param question: User question
    :return: Full evidence to answer the question or a message indicating that evidence is not enough
    """
    # global global_evidence

    final_answer_list = []
    top_scorer_indices = []
    best_scores = []
    evidence_scores = score_evidence(best_answers, question)
    for index, evidence_score in enumerate(evidence_scores):
        if evidence_score.lower() in ["1", "2", "3", "4", "5"]:
            if len(final_answer_list) < 3:
                final_answer_list.append(best_answers[index])
                best_scores.append(int(evidence_score))
                top_scorer_indices.append(index)
            else:
                final_answer_list, best_scores, top_scorer_indices = choose_top3_evidences(
                    best_scores,
                    int(evidence_score), index,
                    top_scorer_indices,
                    final_answer_list,
                    best_answers
                )

    full_evidence = ""

    for single_evidence in final_answer_list:
        full_evidence += single_evidence.page_content + "\n"
    logging.info(f"FULL EVIDENCE: {full_evidence}")
    evidence_checker_result = evidence_checker.run(evidence=full_evidence, question=question)
    logging.info(f"EVIDENCE CHECKER RESULT: {evidence_checker_result}")
    has_enough_evidence = True if evidence_checker_result.upper() == "TRUE" else False
    if has_enough_evidence:
        # global_evidence = full_evidence 
        set_evidence(full_evidence)
        return "Evidence has been successfully gathered"
    else:
        return "Not enough evidence, please gather other results."


def get_evidence(input_data: str | dict | None = None) -> str:
    """
    A function that combines previous functions search_answer, and gather_and_check_evidence to search in vector store and return the most useful evidence
    :param question: The user question
    :return: Full evidence to answer the question or a message indicating that evidence is not enough
    """
    # global global_question
    question = get_question()
    best_search_results = search_answer(question)
    logging.info(f"BEST SEARCH RESULTS: {best_search_results}")
    evidence = gather_and_check_evidence(best_search_results, question)
    return evidence