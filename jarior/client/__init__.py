from datetime import datetime
import json
import logging
__msg_folder__:str=None
__logger__:logging.Logger=None

import os
import pathlib

import threading
__cache__={}
__lock__= threading.Lock()

import time

from setuptools.command.upload_docs import upload_docs


class Context:
    def __init__(self):
        self.info:dict = None
        self.msg_type:str=None
        self.files=[]

def config(msg_folder:str, logger:logging.Logger):
    global __msg_folder__
    global __logger__
    __logger__ = logger

    if msg_folder[0:2]=="./":
        msg_folder = msg_folder[2:msg_folder.__len__()]
        working_dir = str(pathlib.Path(__file__).parent.parent.parent)
        msg_folder= os.path.join(working_dir,msg_folder)
    __msg_folder__ = msg_folder
    if __logger__ is not None:
        __logger__.info(f"Start watch {__msg_folder__}")


    return None

def __get_all_files__(p_dir: str):
    ret=[]

    for path, subdirs, files in os.walk(p_dir):
        for name in files:
            ret+=[os.path.join(path, name)]
    return ret

def watch_run(msg_type, handler):
    global __cache__
    global __lock__
    global __msg_folder__
    if __cache__.get(msg_type) is None:
        __lock__.acquire()
        __cache__[msg_type]=dict()
        __lock__.release()
    files = __get_all_files__(__msg_folder__)
    for k,v in __cache__[msg_type].items():
        if (datetime.utcnow()-v).total_seconds()>240:
            del __cache__[msg_type][k]
    for file in files:
        try:
            if file.split('.')[-2]==msg_type:
                if __cache__[msg_type].get(file) is None:
                    count=0

                    def up_run(_handler,_msg_file):
                        count=0
                        is_ok =False
                        while count<10000 and not is_ok:
                            try:

                                if os.path.isfile(_msg_file):

                                    with open(_msg_file,'r') as fs:
                                        txt_json = fs.read()
                                        full_info_dict= json.loads(txt_json)
                                        del txt_json
                                        _context = Context()
                                        _context.info = full_info_dict.get('info')
                                        _context.files = full_info_dict.get('file_paths')
                                        _context.msg_type = msg_type

                                        _handler(_context)
                                        is_ok =True
                            except Exception as e:
                                pass
                            finally:
                                count=count+1
                                time.sleep(0.1)

                    th=  threading.Thread(target=up_run,args=(handler,file,))
                    th.start()
                    __cache__[msg_type][file] = datetime.utcnow()
        except Exception as e:
            if __logger__ is not None:
                __logger__.debug(e)
            else:
                print(e)

def watch(msg_type,handler,delay_in_second:float)->threading.Thread:

    if not isinstance(delay_in_second,float):
        raise Exception('delay_in_second')
    def loop_watch(msg_type,handler):
        while True:
            time.sleep(delay_in_second)
            watch_run(msg_type,handler)
    ret=threading.Thread(target=loop_watch,args=(msg_type,handler,))
    ret.start()
    return ret