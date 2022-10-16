import logging
import os.path
import pathlib
import threading
from kink import inject
import traceback
import sys
__catch_log__ = dict()
__lock__ = threading.Lock()




def get_logger(logger_name:str, logger_dir:str)-> logging.Logger:
    global __lock__
    global __catch_log__
    if logger_dir[0:2]=="./":
        logger_dir=logger_dir[2:logger_dir.__len__()]
        working_dir = str(pathlib.Path(__file__).parent.parent.parent)
        logger_dir = os.path.join(working_dir,logger_dir)

    if __catch__.get(logger_name) is not None:
        return __catch__.get(logger_name)
    __lock__.acquire()
    try:
        # create logger for prd_ci
        log = logging.Logger(logger_name)
        # log.setLevel(level=logging.INFO)

        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        full_log_dir= os.path.join(logger_dir,"logs","apps",logger_name)
        if not os.path.isdir(full_log_dir):
            os.makedirs(full_log_dir)

        info_handler = logging.FileHandler(os.path.join(full_log_dir,"log.txt"))
        info_handler.setFormatter(formatter)

        log.addHandler(info_handler)
        __catch__[logger_name]=log
        return log
    finally:
        __lock__.release()

@inject
class ELogger:
    def __init__(self):
        self.working_dir=str(pathlib.Path(__file__).parent.parent.parent)
        self.delegate=get_logger("enigma",os.path.join(self.working_dir,"logs"))
    def error(self,e):
        self.delegate.error(e)
    def info(self,e):
        self.delegate.info(e)
    def debug(self,e):
        self.delegate.exception(e)

