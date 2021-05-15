import os
from logging import getLogger, StreamHandler, DEBUG, Formatter

LOGLEVEL = os.getenv("LOGLEVEL", default=DEBUG)


def get_logger(logger_name):
    logger = getLogger(logger_name)
    handler = StreamHandler()
    handler.setFormatter(Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    handler.setLevel(os.getenv("LOGLEVEL", default=LOGLEVEL))
    logger.setLevel(os.getenv("LOGLEVEL", default=LOGLEVEL))
    logger.addHandler(handler)
    logger.propagate = False
    return logger
