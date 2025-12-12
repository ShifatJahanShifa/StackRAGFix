import html
import json
import os
import time

from bs4 import BeautifulSoup as bs
from bs4 import NavigableString
from dotenv import load_dotenv
from stackapi import StackAPI, StackAPIError

from constants.files import (
    JAVASCRIPT_OUTPUT_FILE,
    JAVASCRIPT_STATE_FILE,
    PYTHON_OUTPUT_FILE,
    PYTHON_STATE_FILE,
)
from constants.sites import SITE
from constants.tags import JAVASCRIPT_TAG, PYTHON_TAG

load_dotenv()

STACK_EXCHANGE_API_KEY = os.getenv("STACK_EXCHANGE_API_KEY")
if not STACK_EXCHANGE_API_KEY:
    raise RuntimeError(
        "STACK_EXCHANGE_API_KEY environment variable is not set. Please set it to a valid Stack Exchange API key."
    )


def clean_html_content(html_text):
    soup = bs(html_text, "lxml")
    cleaned = []

    for element in soup.descendants:
        if isinstance(element, NavigableString):
            if element.parent.name == "code":
                # Preserve code block content
                decoded = html.unescape(str(element))
                cleaned.append(f"<code>{decoded}</code>")
            elif element.parent.name not in ["code", "[document]"]:
                cleaned.append(" ".join(element.strip().split()))

    return "\n".join([line for line in " ".join(cleaned).split("\n") if line.strip()])


def load_state(state_file):
    """Load last saved fetch state (page number)."""
    if os.path.exists(state_file):
        with open(state_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_page": 0}


def save_state(page, state_file):
    """Save the current page number to resume later."""
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump({"last_page": page}, f)
    print(f"Saved progress at page {page}")


def save_questions(data, output_file):
    """Append fetched questions to local JSON file."""
    existing = []
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    existing.extend(data)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(data)} new questions (total: {len(existing)})")


def chunk_list(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def fetch_all_answered_questions(site, pagesize, tag, api_key):
    """Continuously fetch all questions that have at least one answer."""

    site_api = StackAPI(site, key=api_key)
    site_api.page_size = pagesize
    state = None
    if tag == PYTHON_TAG:
        state = load_state(PYTHON_STATE_FILE)
    elif tag == JAVASCRIPT_TAG:
        state = load_state(JAVASCRIPT_STATE_FILE)

    start_page = state["last_page"] + 1
    print(f"Resuming from page {start_page}")

    page = start_page
    total = 0

    threads = []
    while True:
        try:
            print(f"\nFetching questions from page {page}...")
            resp = site_api.fetch(
                "search/advanced",
                filter="withbody",
                sort="votes",
                tagged=tag,
                order="desc",
                accepted="true",
                site=site,
                page=page,
            )

            questions = resp.get("items", [])
            if not questions:
                print("No more questions.")
                break

            # Collect only questions that have accepted answers
            accepted_qs = [q for q in questions if "accepted_answer_id" in q]
            if not accepted_qs:
                print("No accepted answers on this page.")
                page += 1
                continue

            accepted_answer_ids = [q["accepted_answer_id"] for q in accepted_qs]

            print(f"Fetching {len(accepted_answer_ids)} accepted answers...")
            # for i in range()
            # answers_resp = site_api.fetch(
            #     f"questions/{';'.join(map(str, accepted_answer_ids))}/answers",
            #     filter="withbody",
            #     sort="votes",
            #     order="desc",
            #     site=site
            # )
            # answers = answers_resp.get("items", [])

            answers = []

            # Split accepted_answer_ids into batches of 100
            for chunk in chunk_list(accepted_answer_ids, 100):
                chunk_str = ";".join(map(str, chunk))
                answers_resp = site_api.fetch(
                    f"answers/{chunk_str}",
                    filter="withbody",
                    # sort="scores",
                    # order="desc",
                    site=site,
                )
                answers.extend(answers_resp.get("items", []))

            # Index answers by their answer_id
            answers_by_id = {a["answer_id"]: a for a in answers}
            print("got answrrs", answers_by_id)

            # # Index answers by their answer_id
            # answers_by_id = {a["answer_id"]: a for a in answers}

            # Merge question with its accepted answer
            qna_pairs = []
            for q in accepted_qs:
                aid = q["accepted_answer_id"]
                accepted_answer = answers_by_id.get(aid)
                if accepted_answer:
                    qna_pairs.append(
                        {
                            "title": q["title"],
                            "question_body": clean_html_content(q["body"]),
                            "link": q["link"],
                            "score": q["score"],
                            "tags": q["tags"],
                            "question_id": q["question_id"],
                            "answer_count": q["answer_count"],
                            "view_count": q["view_count"],
                            "answers": [
                                {
                                    "score": accepted_answer["score"],
                                    "body": clean_html_content(accepted_answer["body"]),
                                }
                            ],
                        }
                    )
                    # qna_pairs["answers"].append({
                    #     "score": accepted_answer["score"],
                    #     "body": clean_html_content(accepted_answer["body"])
                    # })

            if tag == PYTHON_TAG:
                save_questions(qna_pairs, PYTHON_OUTPUT_FILE)
                save_state(page, PYTHON_STATE_FILE)
            elif tag == JAVASCRIPT_TAG:
                save_questions(qna_pairs, JAVASCRIPT_OUTPUT_FILE)
                save_state(page, JAVASCRIPT_STATE_FILE)

            total += len(qna_pairs)

            if not resp.get("has_more", False):
                print("No more pages.")
                break

            backoff = resp.get("backoff")
            if backoff:
                print(f"Backoff {backoff}s")
                time.sleep(backoff)
            else:
                time.sleep(1)

            page += 1

        except StackAPIError as e:
            print(f"StackAPI error: {e}")
            print("Sleeping 30s before retrying…")
            time.sleep(30)
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Sleeping 60s before retrying…")
            time.sleep(60)

    print(f"\n🎯 Finished. Total questions fetched: {total}")


# TODO: tagged should switch between two values. python and javascript
if __name__ == "__main__":
    fetch_all_answered_questions(
        site=SITE, pagesize=100, tag=PYTHON_TAG, api_key=STACK_EXCHANGE_API_KEY
    )
