import pickle

from constants.file_paths import PICKLE_PATH
from utils.logger import logger

logger.info("📌 Loading BM25 retriever (only once at startup)...")
with open(PICKLE_PATH, "rb") as f:
    BM25_RETRIEVER = pickle.load(f)
logger.info("✅ BM25 retriever loaded successfully.")
