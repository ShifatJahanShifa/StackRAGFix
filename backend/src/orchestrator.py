from langchain_pinecone import Pinecone

from sentence_transformers import SentenceTransformer
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain.memory import ConversationBufferMemory

from stackapi import StackAPI
# import config
import json
import ast
import asyncio
import datetime
from typing import List, Dict, Tuple
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.agents import initialize_agent
from langchain.agents import Tool


from langchain.vectorstores import Pinecone

import pinecone

from rank_bm25 import BM25Okapi

from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import random
import os
import logging
from models.model import Model
from src.answer_generator import generate_answer
from src.evidence_scorer import get_evidence
from src.keyword_extractor import generate_keywords
from src.search_and_storage import search_and_store_answers
from models.model_instance import embeddingModel, chatModel
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


# global_evidence = ""
# user_query = ""
# global_unanswered_question_list = []
# global_question_extracted_keywords_dict = {}
# global_generated_answer = ""
# global_question = ""


def generate_full_response(question: str) -> str:
    """
    A function that uses ai-agent to generate a response to the user question
    :param question: User question
    :return: Generated Response
    """
    # global global_question
    # global_question = question 
    set_question(question=question)
    # keyword_extractor_tool = Tool.from_function(
    #     func=generate_keywords,
    #     name="KeywordExtractor",
    #     description="You HAVE TO ALWAYS use this tool as your first step whenever you are given a user-question or a list of questions. Used to extract search terms based on the user question that will be later used to find an answer in stackoverflow. The argument to this function should be the exact user question with no modifications. If given multiple questions, DO NOT separate them. Always enclose it in [] to make it in a python list format"        
    # )


    # search_stack_overflow_tool = Tool.from_function(
    #     func=search_and_store_answers,
    #     name="SearchStackOverflowAndStore",
    #     description="After running KeywordExtractor tool, you NEED to run this tool. Searches in the stackoverflow for an answer using provided search terms. Provide all of the search terms that you have and it will search asynchronously for all of them. Afterwards, it filters the best answers among them and stores their embeddings in Pinecone vector store. This is used to search for an answer later. It returns a string indicating if the data was successfully stored or not"
    # )

    # gather_evidence_tool = Tool.from_function(
    #     func=get_evidence,
    #     name="GatherEvidence",
    #     description="After running SearchStackOverflowAndStore tool, you NEED to run this tool. Searches in our vector store for appropriate answers, filters, and leaves the ones that are useful to answer the question. You either get a message indicating that evidence has been gathered successfully, or a message indicating that there is not enough evidence and you have to start again. "
    # )

    # generate_answer_tool = Tool.from_function(
    #     func=generate_answer,
    #     name="AnswerGenerator",
    #     description="After running GatherEvidence tool, you NEED to run this tool.Takes an input the original question given by the user to generate a well-structured answer that you will use as your result. Your input parameter must be the question specified by the user. The output of this tool is the status indicating if the final answer has been generated successfully or not. If it has been genertaed, finish the chain. No need to output something, just exit the chain with message 'DONE'"
    # )

    # tools = [keyword_extractor_tool, search_stack_overflow_tool, gather_evidence_tool, generate_answer_tool]
    # memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    # agent = initialize_agent(tools, chatModel, agent="zero-shot-react-description", memory=memory, verbose=True)
    # agent.run(question)


    # global global_generated_answer
    # return global_generated_answer

    print("Extracting keywords...")
    keywords = generate_keywords(question)
    if not keywords:
        return "Failed to extract keywords."
    else: 
        print(keywords) 

    # component-2: Search Stack Overflow and store results
    print("Searching StackOverflow...")
    store_status = search_and_store_answers(keywords)
    if "fail" in store_status.lower():
        return "Failed to store StackOverflow answers. Try again." 

    # component-3: Gather evidence
    print("Gathering evidence...")
    evidence = get_evidence()  # input must be in square brackets
    set_evidence(evidence=evidence)
    # if "not enough evidence" in evidence_status.lower():
    #     return "Not enough evidence found. Try rephrasing your question."

    # component-4: Generate the final answer
    print("Generating final answer...")
    answer_status = generate_answer(question)
    if "success" in answer_status.lower() or "done" in answer_status.lower():
        print(f"finale: {get_generated_answer()}")
        return get_generated_answer()

    return "An error occurred during answer generation."

    # return get_generated_answer()
