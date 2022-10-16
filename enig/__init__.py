import logging
import os.path
import pathlib
import threading
from typing import TypeVar, Generic, List
__working_dir__=None
__lock__=threading.Lock()
__catch_log__ ={}
import kink
import yaml
from kink import di
T = TypeVar('T')
__cache_yam_dict__ = {}


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls, *args, **kw)
        return cls._instance
def inject(cls,*args,**kwargs):
    return kink.inject(cls,*args,**kwargs)
def depen(cls:T,*args,**kwargs)->T:
    ret= kink.inject(cls)
    return ret(*args,**kwargs)
def create_instance(cls:T,*args,**kwargs)->T:
    ret = kink.inject(cls)
    return ret(*args, **kwargs)

def get_working_dir():
    global __working_dir__
    global __lock__
    if __working_dir__ is None:
        __lock__.acquire()
        __working_dir__=str(pathlib.Path(__file__).parent.parent)
        __lock__.release()
    return __working_dir__

def load_from_yam_file(path_to_yam_file)->dict:
    """
    Onetime read yaml filr to dict
    On the next time this method will return from cache
    :param path_to_yam_file:
    :return:
    """
    global __cache_yam_dict__
    global __lock__
    p=path_to_yam_file
    if p[0:2]=="./":
        p=p[2:]
        p=os.path.join(get_working_dir(),p).replace('/',os.sep)
    if __cache_yam_dict__.get(p) is None:
        try:
            __lock__.acquire()
            with open(p, 'r') as stream:
                __config__ = yaml.safe_load(stream)
                __cache_yam_dict__[p] = __config__
        finally:
            __lock__.release()

    return __cache_yam_dict__.get(p)
class cls_dict:
    def __init__(self,data:dict):
        self.__data__=data
    def __parse__(self,ret):
        if isinstance(ret, dict):
            return cls_dict(ret)
        if isinstance(ret, list):
            ret_list = []
            for x in ret:
                ret_list += {self.__parse__(x)}
        return ret
    def __getattr__(self, item):
        if item[0:2]=="__" and item[-2:]=="__":
            return self.__dict__.get(item)
        ret= self.__data__.get(item)
        if isinstance(ret,dict):
            return cls_dict(ret)
        if isinstance(ret,list):
            ret_list=[]
            for x in ret:
                ret_list+= {self.__parse__(x)}
            return ret_list
        return ret
def get_logger(logger_name:str="enig", logger_dir:str="./logs")-> logging.Logger:
    global __lock__
    global __catch_log__
    if logger_dir[0:2]=="./":
        logger_dir=logger_dir[2:logger_dir.__len__()]
        working_dir = str(pathlib.Path(__file__).parent.parent.parent)
        logger_dir = os.path.join(working_dir,logger_dir)

    if __catch_log__.get(logger_name) is not None:
        return __catch_log__.get(logger_name)
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
        __catch_log__[logger_name]=log
        return log
    finally:
        __lock__.release()
