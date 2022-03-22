import logging
import sys

logger = logging.getLogger("paper-frame")
consoleLogHandler = logging.StreamHandler(sys.stdout)
consoleLogHandler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)-8s: %(module)s : %(message)s")
)
logger.addHandler(consoleLogHandler)

def get_logging_level(level: str):
    return getattr(logging, level)
