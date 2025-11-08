import os
import src.config
import json   
import ast
import asyncio
import datetime
import random
import logging
# import pinecone
import google.generativeai as genai
# import vertexai
import traceback
from constants.constant import KB_PATH
from stackapi import StackAPI  # class
from dotenv import load_dotenv, find_dotenv
from typing import List, Dict, Tuple
from langchain.prompts import PromptTemplate
from rank_bm25 import BM25Okapi
from datetime import datetime
# from langchain_community.vectorstores import Pinecone
from langchain_pinecone import Pinecone
# from vertexai.language_models import TextEmbeddingModel
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import SentenceTransformerEmbeddings
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


load_dotenv(find_dotenv())

print(os.getenv("GEMINI_API_KEY"))
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
PINECONE_STACK_RAG_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_STACK_RAG_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
PINECONE_STACK_RAG_ENVIRONMENT = os.getenv('PINECONE_ENVIRONMENT')
SO_CLIENT_SECRET = os.getenv('SO_CLIENT_SECRET')
SO_KEY = os.getenv('SO_KEY')


# stackapi object
SITE = StackAPI('stackoverflow', client_secret=SO_CLIENT_SECRET, key=SO_KEY)

# gemini model initialization
llmModel = genai.GenerativeModel("gemini-2.0-flash")

# Load the embedding model
embeddingModel = SentenceTransformer('all-MiniLM-L6-v2')


# Simulated LLMChain for Gemini (LangChain-style wrapper)
class GeminiLLMChain:
    """
    This class is intended to behave **like LangChain’s `LLMChain`**, but it works with the **Gemini API**.
    """
 
    def __init__(self, prompt: PromptTemplate, temperature: float = 0.9):
        self.prompt = prompt
        self.temperature = temperature

    def run(self, **kwargs) -> str:
        promptText = self.prompt.format(**kwargs)
        response = llmModel.generate_content(
            promptText,
            generation_config={"temperature": self.temperature}
        )
        return response.text.strip()

    async def arun(self, **kwargs) -> str:
        promptText = self.prompt.format(**kwargs)
        response = await llmModel.generate_content_async(
            promptText,
            generation_config={"temperature": self.temperature}
        )
        return response.text.strip()

    
# Gemini-based LLM Chains
question_divider = GeminiLLMChain(
    prompt=PromptTemplate.from_template(src.config.QUESTION_DIVIDER_PROMPT), temperature=0.9
)

keyword_extractor = GeminiLLMChain(
    prompt=PromptTemplate.from_template(src.config.KEYWORD_EXTRACTOR_PROMPT), temperature=0.9
)

question_complexity_checker = GeminiLLMChain(
    prompt=PromptTemplate.from_template(src.config.QUESTION_COMPLEXITY_CHECKER_PROMPT), temperature=0.9
)

evidence_scorer = GeminiLLMChain(
    prompt=PromptTemplate.from_template(src.config.EVIDENCE_SCORER_PROMPT), temperature=0.9
)

evidence_checker = GeminiLLMChain(
    prompt=PromptTemplate.from_template(src.config.EVIDENCE_CHECKER_PROMPT), temperature=0.9
)

answer_generator = GeminiLLMChain(
    prompt=PromptTemplate.from_template(src.config.FINAL_ANSWER_GENERATOR_PROMPT), temperature=0.9
)



# 🌍 Global Variables (state)
global_evidence = ""
user_query = ""
global_unanswered_question_list = []
global_question_extracted_keywords_dict = {}
global_generated_answer = ""
global_question = ""


# def get_embeddings(texts: List[str]) -> List[List[float]]:
#     embeddings = embeddingModel.encode(texts)
#     return embeddings

## my embedding model
# embeddingModel = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
embeddingModel = HuggingFaceEmbeddings(model_name="all-mpnet-base-v2")


def get_or_create_eventloop():
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop
        
# ------------------ core functrions from here -------------------------------
def clean_json_string(s: str) -> str:
    if s.startswith("```"):
        lines = s.splitlines()
        # Remove first line if it starts with ```
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        # Remove last line if it is ```
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        return "\n".join(lines).strip()
    return s.strip()

async def async_generate_keywords(question_list: List[str]) -> List[str]:
    """
    A function that asynchronously generates keywords based on the provided list of question
    :param question_list: A list of questions
    :return: A coroutine object, which, when run, returns a list of keywords for each of the provided questions
    """

    tasks = [keyword_extractor.arun(question=question) for question in question_list]
    results = await asyncio.gather(*tasks)
    return results


def generate_keywords(question_list: str) -> List[str]:
    """
    A wrapper function to execute keyword generation (async_generate_keywords) based on the provided list of questions
    :param question_list: A list of questions
    :return: A list of keywords for each of the provided questions
    """
    global user_query
    user_query = question_list

    global global_generated_answer
    global_generated_answer = ""


    question_complexity = question_complexity_checker.run(question=question_list)

    if question_complexity.upper() == "TRUE":
        question_list = question_divider.run(question=question_list)

    try:
        question_list = ast.literal_eval(question_list)
    except Exception as e:
        print(f"❌ Failed to parse question list: {e}")
        return []
    # question_list = ast.literal_eval(question_list)

    # extracted_keyword_list = asyncio.run(async_generate_keywords(question_list))

    # extracted_keyword_list = sum([json.loads(extracted_keyword) for extracted_keyword in extracted_keyword_list], [])

    # extracted_keyword_list = list(set(extracted_keyword_list))

    # return extracted_keyword_list

    loop = get_or_create_eventloop()
    raw_extracted_keyword_list = loop.run_until_complete(async_generate_keywords(question_list))

    # 🔹 Step 4: Decode each keyword JSON safely
    
    import json

    extracted_keyword_list = []
    for idx, raw_item in enumerate(raw_extracted_keyword_list):
        if raw_item:
            cleaned_item = clean_json_string(raw_item)
            try:
                parsed = json.loads(cleaned_item)
                extracted_keyword_list.extend(parsed)
            except json.JSONDecodeError:
                print(f"⚠️ JSON decode error on item {idx}: {cleaned_item!r}")
        else:
            print(f"⚠️ Empty or None response for item {idx}")

        

    # 🔹 Step 5: Remove duplicates
    extracted_keyword_list = list(set(extracted_keyword_list))
    return extracted_keyword_list



#####################  component 2 



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
                dimension=768,  # 👈 use 384 if you're using 'all-MiniLM-L6-v2'
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
    global user_query
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
        scores, top50_questions = bm25_ranker(question_list, user_query, 50)
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


def search_and_store_answers(search_queries: str) -> str:
    """
    A function that combines previously defined functions to search for answers based on the given search queries in stackoverflow, filter them, and store in Pinecone vector store
    :param search_queries: Search terms/keywords used for searching an answer
    :return: A string status indicating if "answers were successfully stored" or "something went wrong with storing answer embeddings, please try again"
    """

    global global_unanswered_question_list
    if isinstance(search_queries, str):
        search_queries = ast.literal_eval(search_queries)

    # search_queries = ast.literal_eval(search_queries)

    initial_answers, question_id_list, unanswered_question_list = search_stackoverflow_new(search_queries)
    if not initial_answers and not question_id_list and not unanswered_question_list:
        return "No questions were found using these keywords, please try again."
    else:
        global_unanswered_question_list = unanswered_question_list

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










#### -------------------------- component 3


# async def async_score_evidence(evidence_list: List[str], question: str) -> List[str]:
#     """
#     A function to asynchronously score all of the retrieved evidences (answers from stack-overflow)
#     :param evidence_list: A list of Stack-overflow answers retrieved from vector store
#     :param question: User given question
#     :return: A coroutine object, which, when run, returns a list of numbers from 1 to 5 indicating the usefulness of each answer to the given question, with higher indicating better, or "not useful" if the answer is not useful at all
#     """
#     logging.info("---"*100)
#     for evidence in evidence_list:
#         logging.info(f"CURRENT EVIDENCE: {evidence.page_content}")
#         logging.info(f"QUESTION: {question}")
#     score_tasks = [evidence_scorer.arun(evidence=evidence.page_content, question=question) for evidence in evidence_list]
#     results = await asyncio.gather(*score_tasks)
#     return results


async def async_score_evidence(evidence_list: List[str], question: str) -> List[str]:
    """
    Asynchronously score all evidences one by one with a delay to avoid quota limits.
    """
    results = []
    for evidence in evidence_list:
        logging.info(f"CURRENT EVIDENCE: {evidence.page_content}")
        logging.info(f"QUESTION: {question}")

        result = await evidence_scorer.arun(evidence=evidence.page_content, question=question)
        results.append(result)

        # Wait 1 second before next call to avoid quota limit
        await asyncio.sleep(1)

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
    loop = asyncio.get_event_loop()
    evidence_score_list = loop.run_until_complete(async_score_evidence(evidence_list, question))

    return evidence_score_list


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
    global global_evidence

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
        global_evidence = full_evidence
        return "Evidence has been successfully gathered"
    else:
        return "Not enough evidence, please gather other results."


def get_evidence(question: str) -> str:
    """
    A function that combines previous functions search_answer, and gather_and_check_evidence to search in vector store and return the most useful evidence
    :param question: The user question
    :return: Full evidence to answer the question or a message indicating that evidence is not enough
    """
    global global_question
    question = global_question
    best_search_results = search_answer(question)
    logging.info(f"BEST SEARCH RESULTS: {best_search_results}")
    evidence = gather_and_check_evidence(best_search_results, question)
    return evidence




# ### ---------------------------------- component 4

def generate_answer(question: str) -> str:
    """
    A function that uses answer generator llm to generate an answer based on the gathered evidence and the given question
    :param question: User given question
    :return: Answer to the user question
    """
    try:
        global global_evidence
        global global_unanswered_question_list
        global global_generated_answer
        generated_answer = answer_generator.run(question=question, evidence=global_evidence, unanswered_question_list=global_unanswered_question_list)
        global_generated_answer = generated_answer

        if generated_answer:
            return "Answer has been successfully generated"
        else:
            return "We were not able to generate the final answer, please try again."
    except Exception as e:
        logging.error(f"Something went wrong while generating an answer: {e}")



# ----------------------- testing

def generate_response(question: str) -> str: 
    """
    A function that uses ai-agent to generate a response to the user question
    :param question: User question
    :return: Generated Response
    """
    global global_question
    global_question=json.dumps([question])
    print(global_question)
    
    # component-1: Extract keywords
    print("Extracting keywords...")
    keywords = generate_keywords(global_question)
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
    evidence_status = get_evidence(f"[{question}]")  # input must be in square brackets
    if "not enough evidence" in evidence_status.lower():
        return "Not enough evidence found. Try rephrasing your question."

    # component-4: Generate the final answer
    print("Generating final answer...")
    answer_status = generate_answer(question)
    if "success" in answer_status.lower() or "done" in answer_status.lower():
        return global_generated_answer

    return "An error occurred during answer generation."

# generate_response("ast")

# print(global_generated_answer)

# if __name__ == "__main__":
#     question = "How do I prevent memory leaks in a Python multi-threaded application?"

#     # Example: Use keyword extractor chain
#     keywords = keyword_extractor.run(question=question)
#     print("Extracted Keywords:\n", keywords)

#     # Example: Get SentenceTransformers embeddings
#     embeddings = get_embeddings(["What is Python?", "Explain garbage collection in Python."])
#     print("Embeddings:\n", embeddings)

# # embeddings model initialization 
# vertexai.init(
#     project="gen-lang-client-0394030894",
#     location="us-central1"
# )

# EmbeddingModel = TextEmbeddingModel.from_pretrained("textembedding-gecko@latest")



# Encode your text
# sentences = ["What is Python?"]
# embeddings = EmbeddingModel.encode(sentences)

# # Example: Print shape and first few values
# print(embeddings.shape)       # e.g., (1, 384)
# print(embeddings[0][:5])      # f

# # testing
# response = model.generate_content("today is one of the biggest festivals of muslims. tell me what is that?")
# print(response.text)





# GEMINI_API_KEY=os.getenv('GEMINI_API_KEY')
# SO_CLIENT_SECRET=os.getenv('SO_CLIENT_SECRET')
# SO_KEY=os.getenv('SO_KEY')

# # gemini model instantiation 
# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash",temperature=0.9)
# # llm.invoke("Write me a ballad about LangChain")
# help(StackAPI)
# # StackAPI('stackoverflow','2.3',SO_CLIENT_SECRET,key=SO_KEY)

# import google.generativeai as genai

# genai.configure(api_key="YOUR_API_KEY")

# model = genai.GenerativeModel("gemini-pro")
# response = model.generate_content("What is LangChain?")
# print(response.text)


