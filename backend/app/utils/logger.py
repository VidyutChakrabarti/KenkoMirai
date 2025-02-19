import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("covid_simulation")

def log_info(message):
    logger.info(message)
