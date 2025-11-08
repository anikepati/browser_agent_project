import logging
import json
from config import AppConfig

def setup_logging():
    level = logging.DEBUG if AppConfig.ENV_MODE == 'dev' else logging.INFO
    logging.basicConfig(level=level, filename=AppConfig.LOG_FILE, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
    # Structured logging for enterprise (e.g., JSON for ELK)
    def json_log(msg, extra=None):
        log_entry = {"message": msg, **(extra or {})}
        logger.info(json.dumps(log_entry))
    
    logger.json_log = json_log
    return logger
