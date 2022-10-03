import json
import logging
__msg_folder__:str=None
__logger__:logging.Logger=None

import os


import threading
__cache__={}
__lock__= threading.Lock()

import time
class Context:
    def __init__(self):
        self.info:dict = None
        self.msg_type:str=None
        self.files=[]

def config(msg_folder:str, logger:logging.Logger):
    global __msg_folder__
    global __logger__
    __logger__ = logger
    __msg_folder__ =msg_folder
    if __logger__ is not None:
        __logger__.info(f"Start watch {msg_folder}")


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
    for file in files:
        try:
            if file.split('.')[-2]==msg_type:
                if __cache__[msg_type].get(file) is None:
                    __cache__[msg_type][file]=file
                    with open(file,'r') as fs:
                        txt_json = fs.read()
                        full_info_dict= json.loads(txt_json)
                        contex = Context()
                        contex.info = full_info_dict.get('info')
                        contex.files = full_info_dict.get('file_paths')
                        contex.msg_type = msg_type
                        th= threading.Thread(target=handler,args=(contex,))
                        th.start()
        except Exception as e:
            if __logger__ is not None:
                __logger__.debug(e)
            else:
                print(e)

def watch(msg_type,handler)->threading.Thread:
    def loop_watch(msg_type,handler):
        while True:
            time.sleep(0.001)
            watch_run(msg_type,handler)
    ret=threading.Thread(target=loop_watch,args=(msg_type,handler,))
    ret.start()
    return ret