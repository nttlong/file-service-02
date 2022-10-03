import logging
import threading
import pathlib
import os

logger = logging.getLogger("fastapi")
__cache__ = {}
__lock__ = threading.Lock()

__log_dir__ = os.path.join(pathlib.Path(__file__).parent.parent, "logs")
if not os.path.isdir(__log_dir__):
    os.makedirs(__log_dir__)

def get_logger(name: str) -> logging.Logger:
    global __cache__
    global __lock__
    global __log_dir__
    ret = __cache__.get(name.lower())
    if ret is not None:
        return ret
    try:
        __lock__.acquire()
        ful_path_to_log = os.path.join(__log_dir__, f"{name.lower()}.txt")
        ret = logging.getLogger(name.lower())
        ret.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s : %(name)s : %(message)s')
        file_handler = logging.FileHandler(ful_path_to_log)
        file_handler.setFormatter(formatter)
        ret.addHandler(file_handler)
    finally:
        __lock__.release()
        return ret
