# pip install StackAPI
from stackapi import StackAPI, StackAPIError
import time
import json
import os

STATE_FILE = "fetch_state.json"
OUTPUT_FILE = "stackoverflow_questions.json"

def load_state():
    """Load last saved fetch state (page number)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_page": 0}

def save_state(page):
    """Save the current page number to resume later."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_page": page}, f)
    print(f"💾 Saved progress at page {page}")

def save_questions(data):
    """Append fetched questions to local JSON file."""
    existing = []
    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    existing.extend(data)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=4, ensure_ascii=False)
    print(f"✅ Saved {len(data)} new questions (total: {len(existing)})")

def fetch_all_answered_questions(site="stackoverflow", pagesize=100, api_key=None):
    """Continuously fetch all questions that have at least one answer."""
    site_api = StackAPI(site, key=api_key)
    site_api.page_size = pagesize

    state = load_state()
    start_page = state["last_page"] + 1
    print(f"▶️ Resuming from page {start_page}")

    page = start_page
    total = 0

    while True:
        try:
            print(f"\nFetching page {page} …")
            resp = site_api.fetch(
                "questions",
                filter="!)rTk(f1hwP1_gXf3kM",
                sort="creation",
                order="desc",
                answers=1,
                site=site,
                page=page
            )

            items = resp.get("items", [])
            if not items:
                print("⚠️ No items found. Possibly reached end or API issue.")
                break

            save_questions(items)
            total += len(items)
            save_state(page)

            if not resp.get("has_more", False):
                print("✅ No more pages. Completed fetching.")
                break

            # handle backoff if requested
            backoff = resp.get("backoff")
            if backoff:
                print(f"⏳ Backoff {backoff}s")
                time.sleep(backoff)
            else:
                time.sleep(1)

            page += 1

        except StackAPIError as e:
            print(f"❌ StackAPI error: {e}")
            print("Sleeping 30s before retrying…")
            time.sleep(30)
        except Exception as e:
            print(f"Unexpected error: {e}")
            print("Sleeping 60s before retrying…")
            time.sleep(60)

    print(f"\n🎯 Finished. Total questions fetched: {total}")


if __name__ == "__main__":
    API_KEY = "YOUR_API_KEY_HERE"  # optional
    fetch_all_answered_questions(
        site="stackoverflow",
        pagesize=100,
        api_key=API_KEY
    )
