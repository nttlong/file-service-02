import json
import logging

__msg_folder__: str = None
__file_folder__: str = None
__logger__: logging.Logger = None
__age_of_msg__: int = 1

import os.path
import datetime
import pathlib
import threading
__lock__ = threading.Lock()

def __get_all_files__(p_dir: str):
    ret=[]
    for path, subdirs, files in os.walk(p_dir):
        for name in files:
            ret+=[os.path.join(path, name)]
    return ret


def __get_utc_time_of_file__(file_path):
    dt = os.path.getmtime(file_path)
    return datetime.datetime.utcfromtimestamp(dt)


def __get_age_of_file_in_minutes__(file_path):
    create_time = __get_utc_time_of_file__(file_path)
    return (datetime.datetime.utcnow() - create_time).total_seconds() / 60


def __thead_clean_up__(logger: logging.Logger = None):
    def run(logs):
        try:
            global __msg_folder__
            global __age_of_msg__
            files = __get_all_files__(__msg_folder__)
            for file in files:
                age = __get_age_of_file_in_minutes__(file)
                if age > __age_of_msg__:
                    try:
                        os.remove(file)
                        if isinstance(logs, logging.Logger):
                            logs.info(f"Delete {file}")
                    except Exception as e:
                        logger.debug(e)
        except Exception as e:
            if isinstance(logger, logging.Logger):
                logger.debug(e)
            else:
                print(e)
    try:
        if isinstance(logger, logging.Logger):
            logger.info(f"Clean up start any file older than {__age_of_msg__} minutes will be deleted")
        threading.Thread(target=run, args=(logger,)).start()
        if isinstance(logger, logging.Logger):
            logger.info(f"Clean up start")
    except Exception as e:
        if isinstance(logger, logging.Logger):
            logger.debug(e)
        else:
            raise e


def config(
        msg_folder: str,
        file_folder: str,
        age_of_msg_in_minutes: int = 1, logger: logging.Logger = None):
    """
    Set up a config
    :param msg_folder: The folder of msg
    :param file_folder: The folder of content file
    :param age_of_msg_in_minutes: Clean if the age of  msg log file older than
    :param logger:
    :return:
    """
    try:
        global __msg_folder__
        global __file_folder__
        global __logger__
        global __age_of_msg__
        if __file_folder__ is not None:
            return
        try:
            __lock__.acquire()
            woring_dir = str(pathlib.Path(__file__).parent.parent)
            if msg_folder[0:2]=="./":
                msg_folder = msg_folder[2:msg_folder.__len__()]
                msg_folder=os.path.join(woring_dir,msg_folder)
                if not os.path.isdir(msg_folder):
                    os.makedirs(msg_folder)

            __msg_folder__ = msg_folder
            if msg_folder[0:2]=="./":
                msg_folder = msg_folder[2:msg_folder.__len__()]
                msg_folder=os.path.join(woring_dir,msg_folder)
                if not os.path.isdir(msg_folder):
                    os.makedirs(msg_folder)
            __file_folder__ = file_folder
            __age_of_msg__ = age_of_msg_in_minutes
            __logger__ = logger
            if not os.path.isdir(__msg_folder__):
                os.makedirs(__msg_folder__)
            if not os.path.isdir(__file_folder__):
                os.makedirs(__file_folder__)
            __thead_clean_up__(logger)
        finally:
            __lock__.release()
    except Exception as e:
        if isinstance(logger,logging.Logger):
            logger.debug(e)
        else:
            raise e
    return None


def commit(msg_id:str,msg_type:str, info:dict, files_path):
    global __logger__
    def runner():
        global __msg_folder__
        global __logger__
        try:
            full_info= dict(
                info=info,
                file_paths=files_path
            )
            full_msg=os.path.join(__msg_folder__,f"{msg_id}.{msg_type}.json")
            str_content=json.dumps(full_info)
            with open(full_msg,"w") as fs:
                fs.write(str_content)
        except Exception as e:
            if __logger__ is not None:
                __logger__.debug(e)
            else:
                raise e
    try:
        th=threading.Thread(target=runner,args=())
        th.start()
    except Exception as e:
        if __logger__ is not None:
            __logger__.debug(e)
        else:
            raise e
    return None