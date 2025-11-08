import ast
import asyncio
import json
import logging
# import config
from src.llm_chain import question_complexity_checker, question_divider, keyword_extractor
from dotenv import load_dotenv, find_dotenv
from datetime import datetime
import random
import os
import logging
# from backend.models.model import Model
# from langchain.vectorstores import Pinecone
from langchain_pinecone import Pinecone
from pinecone import Pinecone as PineconeClient, ServerlessSpec
# import pinecone
import traceback

from rank_bm25 import BM25Okapi


from stackapi import StackAPI

from typing import Dict, List, Tuple
# from backend.models.model import Model
from constants.constant import KB_PATH
from models.model_instance import embeddingModel

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


def bm25_ranker(corpus: List[str], query: str, n: int) -> Tuple[List[float], List[str]]:
    """
    A function that uses bm25 algorithm to rerank the provided questions based on their relevance to the given query and choose top n among them
    :param corpus: The corpus or the list of questions that construct the corpus which later will be scored and re-reanked
    :param query: The given query based on which questions must be re-ranked
    :param n: The number of questions that must be returned
    :return: A tuple consisting of scores of each document as well as top-n questions
    """
    tokenized_corpus = [doc.split(" ") for doc in corpus]

    bm25 = BM25Okapi(tokenized_corpus)

    tokenized_query = query.split()

    doc_scores = bm25.get_scores(tokenized_query)

    top_n = bm25.get_top_n(tokenized_query, corpus, n=n)
    return doc_scores, top_n


def search_stackoverflow_new(search_queries):
    """
    A function to search for answers in stackoverflow based on search queries
    :param search_queries: A list of search queries that will be used for searching in stackoverflow
    :return: A list of answers. Each element in the list contains question key with question details as well as answer key with answer details
    """
    # global user_query
    question_id_list = []
    search_queries = list(set(search_queries))
    question_list = []
    question_id_dict = {}
    question_accepted_answer_dict = {}
    question_detail_dict = {}
    full_temp_list = []
    unanswered_question_list = []
    filepath = KB_PATH
    stored_question_id_dict = {}
    stored_question_id_list = []
    if os.path.exists(filepath):
        with open(filepath, 'r') as file:
            stored_question_id_dict = json.load(file)
            stored_question_id_list = stored_question_id_dict.get("questions")
    for search_query in search_queries:
        questions = SITE.fetch('search/advanced', q=search_query, filter='withbody')

        for question in questions.get("items", []):

            if question.get("is_answered"):
                question_id = question.get('question_id')
                accepted_answer_id = question.get('accepted_answer_id')
                if question_id not in question_id_list:

                    question_detail_dict[question_id] = {
                        "user_id": question.get("owner").get("user_id"),
                        "profile_link": question.get("owner").get("link"),
                        "answer_view_count": question.get("view_count"),
                        "accepted_answer_id": question.get("accepted_answer_id"),
                        "creation_date": datetime.utcfromtimestamp(question.get("creation_date")).strftime(
                            '%Y-%m-%d %H:%M:%S'),
                        "link": question.get("link"),
                        "title": question.get("title"),
                        "body": question.get("body")
                    }
                    question_id_list.append(question_id)
                    full_question = f"Title: {question['title']}\nBody: {question['body']}"
                    question_list.append(full_question)
                    question_id_dict[full_question] = question_id
                    question_accepted_answer_dict[question_id] = accepted_answer_id

    if question_list:
        scores, top50_questions = bm25_ranker(question_list, get_user_query(), 50)
        final_question_answer_dict = {}
        for top_question in top50_questions:
            current_question_id = question_id_dict.get(top_question)
            if current_question_id:
                final_question_answer_dict[current_question_id] = question_accepted_answer_dict.get(current_question_id)
        for question_id, accepted_answer_id in final_question_answer_dict.items():
            current_question_answer_dict = {}
            if accepted_answer_id:
                if question_id not in stored_question_id_list:
                    answers = SITE.fetch('questions/{}/answers'.format(question_id), filter='withbody')

                    for answer in answers['items']:
                        answer_details = {
                            "user": answer.get("owner").get("user_id"),
                            "user_reputation": answer.get("owner").get("reputation"),
                            "profile_link": answer.get("owner").get("link"),
                            "is_accepted": answer.get("is_accepted"),
                            "score": answer.get("score"),
                            "creation_date": datetime.utcfromtimestamp(answer.get("creation_date")).strftime(
                                '%Y-%m-%d %H:%M:%S'),
                            "body": answer.get("body")}
                        if current_question_answer_dict.get("answers"):
                            current_question_answer_dict["answers"].append(answer_details)
                        else:
                            current_question_answer_dict["answers"] = [answer_details]
                    full_temp_list.append(
                        {"question": question_detail_dict[question_id], "answers": current_question_answer_dict.get("answers")})
            else:
                current_question_details = question_detail_dict.get(question_id)
                if current_question_details:
                    current_question = f"""\nQuestion Title: {current_question_details.get("title")}\nQuestion Link: {current_question_details.get("link")}\n"""
                    unanswered_question_list.append(current_question)

        return full_temp_list, question_id_list, unanswered_question_list
    else:
        return "", "", ""
    

def choose_top2_unaccepted_answers(current_unaccepted_1: Dict, current_unaccepted_2: Dict, new_unaccepted: Dict) -> List[Dict]:
    """
    A function to choose top 2 unaccepted answers from stack-overflow from the provided 3 based on their scores and date
    :param current_unaccepted_1: One of the current top 2 answers
    :param current_unaccepted_2: One of the current top 2 answers
    :param new_unaccepted: new candidate answer
    :return: An updated list of top 2 answers
    """

    top2_list = []

    if current_unaccepted_1.get("score") > current_unaccepted_2.get("score") and new_unaccepted.get(
            "score") > current_unaccepted_2.get("score"):
        top2_list = [current_unaccepted_1, new_unaccepted]
    elif current_unaccepted_2.get("score") > current_unaccepted_1.get("score") and new_unaccepted.get(
            "score") > current_unaccepted_1.get("score"):
        top2_list = [current_unaccepted_2, new_unaccepted]
    elif current_unaccepted_1.get("score") > new_unaccepted.get("score") and current_unaccepted_2.get(
            "score") > new_unaccepted.get("score"):
        top2_list = [current_unaccepted_1, current_unaccepted_2]
    elif current_unaccepted_1.get("score") > new_unaccepted.get("score") and new_unaccepted.get(
            "score") == current_unaccepted_2.get("score"):
        top2_list.append(current_unaccepted_1)
        if datetime.strptime(new_unaccepted.get("creation_date"), "%Y-%m-%d %H:%M:%S") > datetime.strptime(
                current_unaccepted_2.get("creation_date"), "%Y-%m-%d %H:%M:%S"):
            top2_list.append(new_unaccepted)
        else:
            top2_list.append(current_unaccepted_2)
    elif current_unaccepted_2.get("score") > new_unaccepted.get("score") and new_unaccepted.get(
            "score") == current_unaccepted_1.get("score"):
        top2_list.append(current_unaccepted_2)
        if datetime.strptime(new_unaccepted.get("creation_date"), "%Y-%m-%d %H:%M:%S") > datetime.strptime(
                current_unaccepted_1.get("creation_date"), "%Y-%m-%d %H:%M:%S"):
            top2_list.append(new_unaccepted)
        else:
            top2_list.append(current_unaccepted_1)
    elif new_unaccepted.get("score") > current_unaccepted_1.get("score") and current_unaccepted_2.get(
            "score") == current_unaccepted_1.get("score"):
        top2_list.append(new_unaccepted)
        if datetime.strptime(current_unaccepted_1.get("creation_date"), "%Y-%m-%d %H:%M:%S") > datetime.strptime(
                current_unaccepted_2.get("creation_date"), "%Y-%m-%d %H:%M:%S"):
            top2_list.append(current_unaccepted_1)
        else:
            top2_list.append(current_unaccepted_2)
    elif current_unaccepted_2.get("score") == current_unaccepted_1.get("score") and current_unaccepted_2.get("score") == new_unaccepted.get("score"):
        top2_list = random.choices([current_unaccepted_1, current_unaccepted_2, new_unaccepted], k=2)

    top2_full_list = {"not_accepted_answer_body": [], "not_accepted_answer_date": []}
    for current_answer in top2_list:
        top2_full_list["not_accepted_answer_body"].append(current_answer.get("body"))
        top2_full_list["not_accepted_answer_date"].append(
            current_answer.get("creation_date")
        )
    return top2_full_list

def filter_and_process_answers(question_answer_list: List[Dict]) -> List[Dict]:
    """
    A function to filter and process answers from stack-overflow
    :param question_answer_list: A list of questions and their answers with their corresponding details (question owner, date, answer body, etc.)
    :return: A filtered and processed question-answer list with details, and unanswered questions with their links that might be useful
    """

    processed_answers = []

    for question_answer_pair in question_answer_list:
        current_processed_answer = {}

        question = question_answer_pair.get("question")
        answers = question_answer_pair.get("answers")
        top2_full_answers = []

        for answer in answers:
            current_processed_answer["question_title"] = question.get("title")
            current_processed_answer["question_link"] = question.get("link")
            if answer.get("is_accepted"):
                if answer.get("is_accepted") == True:
                    current_processed_answer["accepted_answer_body"] = answer.get("body")
                    current_processed_answer["accepted_answer_date"] = answer.get("creation_date")
            else:
                if not current_processed_answer.get("not_accepted_answer_body"):
                    current_processed_answer["not_accepted_answer_body"] = [answer.get("body")]
                    current_processed_answer["not_accepted_answer_date"] = [answer.get("creation_date")]
                    top2_full_answers.append(answer)

                else:
                    if len(current_processed_answer["not_accepted_answer_date"]) < 2:
                        current_processed_answer["not_accepted_answer_body"].append(answer.get("body"))
                        current_processed_answer["not_accepted_answer_date"].append(answer.get("creation_date"))
                        top2_full_answers.append(answer)

                    else:
                        top2_unaccepted = choose_top2_unaccepted_answers(top2_full_answers[0], top2_full_answers[1], answer)
                        current_processed_answer["not_accepted_answer_date"] = top2_unaccepted
        processed_answers.append(current_processed_answer)

    return processed_answers


def store_answers_embeddings(processed_answers: List[Dict]) -> str:
    """
    A function to create and store answer embeddings in Pinecone Vector Store
    :param processed_answers: Processed answers that need to be stored
    :return: A string status indicating if "answers were successfully stored" or "something went wrong with storing answer embeddings"
    """

    answer_strings = []
    for question_answer_pair in processed_answers:
        current_answer_string = f"""\nQuestion Title: {question_answer_pair.get("question_title")}\nQuestion Link: {question_answer_pair.get("question_link")}\n"""

        if question_answer_pair.get("accepted_answer_body"):
            current_answer_string += f"""\nAccepted Answer:\n{question_answer_pair.get("accepted_answer_body")}\n"""

        if question_answer_pair.get("not_accepted_answer_body"):
            for unaccepted_answer in question_answer_pair.get(
                "not_accepted_answer_body"
            ):
                current_answer_string += f"""\nNOT Accepted Answer:\n{unaccepted_answer}\n"""

        answer_strings.append(current_answer_string)

    # try:
    #     pinecone.init(
    #         api_key=PINECONE_STACK_RAG_API_KEY,
    #         environment=PINECONE_STACK_RAG_ENVIRONMENT
    #     )

    #     index_name = PINECONE_STACK_RAG_INDEX_NAME

    #     logging.info("Started loading Stack Overflow answers into Pinecone")
    #     Pinecone.from_texts(answer_strings, embeddingModel, index_name=index_name)
    #     logging.info("Successfully loaded Stack Overflow answers into Pinecone")

    #     return "Answers have been successfully stored."
    # except Exception as e:
    #     logging.error("Something went wrong while storing Stack Overflow answers into Pinecone", e)
    #     return "Something went wrong with storing answer embeddings, please try again."
    try:
        # pinecone.init(
        #     api_key=PINECONE_STACK_RAG_API_KEY,
        #     environment=PINECONE_STACK_RAG_ENVIRONMENT
        # )

        # index_name = PINECONE_STACK_RAG_INDEX_NAME 

        pc = PineconeClient(api_key=PINECONE_STACK_RAG_API_KEY)

        # # Create index if it doesn't exist
        if PINECONE_STACK_RAG_INDEX_NAME not in pc.list_indexes().names():
            pc.create_index(
                name=PINECONE_STACK_RAG_INDEX_NAME,
                dimension=1024,  # 👈 use 384 if you're using 'all-MiniLM-L6-v2'
                metric='cosine',
                spec=ServerlessSpec(cloud='aws', region='us-west-2')  # update region if needed
            )

        # Connect to index
        index_name = PINECONE_STACK_RAG_INDEX_NAME
        # index_name.delete(delete_all=True)
        index = pc.Index(PINECONE_STACK_RAG_INDEX_NAME)
        # index.delete(delete_all=True)


        logging.info("Started loading Stack Overflow answers into Pinecone")
        Pinecone.from_texts(answer_strings, embeddingModel, index_name=index_name)
        logging.info("Successfully loaded Stack Overflow answers into Pinecone")

        return "Answers have been successfully stored."
    except Exception as e:
        logging.error("Something went wrong while storing Stack Overflow answers into Pinecone")
        logging.error(traceback.format_exc()) 
        return "Something went wrong with storing answer embeddings, please try again."




def search_and_store_answers(search_queries: str) -> str:
    """
    A function that combines previously defined functions to search for answers based on the given search queries in stackoverflow, filter them, and store in Pinecone vector store
    :param search_queries: Search terms/keywords used for searching an answer
    :return: A string status indicating if "answers were successfully stored" or "something went wrong with storing answer embeddings, please try again"
    """

    # global global_unanswered_question_list
    search_queries=f"{search_queries}"
    print(search_queries)
    search_queries = ast.literal_eval(search_queries)

    initial_answers, question_id_list, unanswered_question_list = search_stackoverflow_new(search_queries)
    if not initial_answers and not question_id_list and not unanswered_question_list:
        return "No questions were found using these keywords, please try again."
    else:
        # global_unanswered_question_list = unanswered_question_list
        set_unanswered_question_list(unanswered_question_list=unanswered_question_list)

        logging.info(f"SEARCH STACKOVERFLOW RESULTS: {initial_answers}")
        filtered_answers = filter_and_process_answers(initial_answers)

        store_status = store_answers_embeddings(filtered_answers)

        filepath = KB_PATH
        stored_question_id_list = {}
        if os.path.exists(filepath):
            with open(filepath, 'r') as file:
                stored_question_id_list = json.load(file)
        else:
            logging.error(f"{filepath} FILE DOES NOT EXIST")
        if stored_question_id_list.get("questions"):
            stored_question_id_list["questions"].extend(question_id_list)
        else:
            stored_question_id_list["questions"] = question_id_list
        with open(filepath, 'w') as file:
            json.dump(stored_question_id_list, file)

        return store_status