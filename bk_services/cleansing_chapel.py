"""
This processing clean up temporary file which is older than 48 hours from now
"""
import os.path
import pathlib
import os
import datetime
import sys
import threading
import time
sys.path.append(str(pathlib.Path(__file__).parent))
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from jarior.loggers import get_logger
logger = get_logger(
    logger_name= pathlib.Path(__file__).stem,
    logger_dir= str(pathlib.Path(__file__).parent.parent)
)
def __get_all_files__(p_dir: str):
    ret=[]
    for path, subdirs, files in os.walk(p_dir):
        for name in files:
            ret+=[os.path.join(path, name)]
    return ret
working_dir = str(pathlib.Path(__file__).parent.parent)
tmp_dir = os.path.join(working_dir,"tmp")
limit_age= 24*60*2
def __get_utc_time_of_file__(file_path):
    dt = os.path.getmtime(file_path)
    return datetime.datetime.utcfromtimestamp(dt)
def __get_age_of_file_in_minutes__(file_path):
    create_time = __get_utc_time_of_file__(file_path)
    return (datetime.datetime.utcnow() - create_time).total_seconds() / 60
def run():
    global tmp_dir
    global limit_age
    global logger
    try:
        files = __get_all_files__(tmp_dir)
        for file in files:
            try:
                age = __get_age_of_file_in_minutes__(file)
                if age>limit_age:
                    os.remove(file)
                    logger.info(f"Delete file {file}")
            except Exception as e:
                logger.debug(e)
    except Exception as e:
        logger.debug(e)

def running():
    delay_time = 60*60*8
    while True:
        run()
        time.sleep(delay_time)
th = threading.Thread(target=running,args=())
th.start()
th.join()