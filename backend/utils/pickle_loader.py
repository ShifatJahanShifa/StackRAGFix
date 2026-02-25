import pickle

from constants.file_paths import JS_PICKLE_PATH, PY_PICKLE_PATH
from utils.logger import logger

logger.info("Loading BM25 retriever (only once at startup)...")
# for python
with open(PY_PICKLE_PATH, "rb") as f:
    PY_BM25_RETRIEVER = pickle.load(f)
logger.info("BM25 retriever loaded successfully.")


# for javascript
with open(JS_PICKLE_PATH, "rb") as f:
    JS_BM25_RETRIEVER = pickle.load(f)
logger.info("BM25 retriever loaded successfully.")
