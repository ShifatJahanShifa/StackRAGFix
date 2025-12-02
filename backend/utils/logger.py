import logging

logging.basicConfig(
    level=logging.INFO,  # default log level
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)
