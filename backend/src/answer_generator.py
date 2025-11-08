import ast
import asyncio
import json
import logging
import src.config
from src.llm_chain import answer_generator
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import random
import os
import logging
# from backend.models.model import Model
# from langchain.vectorstores import Pinecone
# from langchain_pinecone import Pinecone

# import pinecone

from rank_bm25 import BM25Okapi


from stackapi import StackAPI

from typing import Dict, List, Tuple


# global lgbe...
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
from models.model_instance import embeddingModel, chatModel

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


def generate_answer(question: str) -> str:
    """
    A function that uses answer generator llm to generate an answer based on the gathered evidence and the given question
    :param question: User given question
    :return: Answer to the user question
    """
    try:
        # global global_evidence
        # global global_unanswered_question_list
        # global global_generated_answer
        generated_answer = answer_generator.run(question=question, evidence=get_evidence(), unanswered_question_list=get_unanswered_question_list())
        # global_generated_answer = generated_answer
        set_generated_answer(generated_answer)
        print(f" seeee: {generated_answer}")
        print(f"see the answer: {get_generated_answer()}")

        if generated_answer:
            return "success"
        else:
            return "We were not able to generate the final answer, please try again."
    except Exception as e:
        logging.error(f"Something went wrong while generating an answer: {e}")