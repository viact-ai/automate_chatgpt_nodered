import logging
import sys


def get_logger(name):
    # create logger that log to file and stdout with the same format
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.hasHandlers():
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)s %(filename)s %(funcName)s (%(lineno)d) %(message)s")
        shandler = logging.StreamHandler(sys.stdout)
        shandler.setFormatter(formatter)
        logger.addHandler(shandler)

        fhandler = logging.FileHandler("log/app.log")
        fhandler.setFormatter(formatter)
        logger.addHandler(fhandler)

    return logger
