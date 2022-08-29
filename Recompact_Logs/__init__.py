import logging, logging.handlers

import os
from pathlib import Path

dir_path = Path(os.path.abspath(__file__)).parent.parent.absolute()
log_dir = os.path.join(str(dir_path), "logs")
if not os.path.isdir(log_dir):
    os.mkdir(log_dir)


def get_logger(rel_path):
    global log_dir
    rel_path=rel_path.replace('.',os.sep)
    logger = logging.getLogger(rel_path)
    logger.setLevel(logging.INFO)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s : %(message)s')
    log_location = os.path.join(log_dir, rel_path)
    if not os.path.isdir(log_location):
        os.makedirs(log_location)
    file_handler = logging.FileHandler(os.path.join(log_location, "log.txt"))
    file_handler.setFormatter(formatter)

    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.addHandler(file_handler)
    return logger
