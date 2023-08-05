import logging
import sys

LOG = logging.getLogger("paper-frame")
consoleLogHandler = logging.StreamHandler(sys.stdout)
consoleLogHandler.setFormatter(
    logging.Formatter("[%(asctime)s] %(levelname)-8s: %(module)s : %(message)s")
)
LOG.addHandler(consoleLogHandler)


def init_logger(log_level: str):
    LOG.setLevel(logging.getLevelName(log_level))
