import logging
from config import AppConfig

def setup_logging():
    logging.basicConfig(level=logging.INFO, filename=AppConfig.LOG_FILE, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    return logger
