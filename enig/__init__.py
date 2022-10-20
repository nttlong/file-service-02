import logging
import os.path
import pathlib
import sys
import threading
from typing import TypeVar, Generic, List
__working_dir__=None
__lock__=threading.Lock()
__catch_log__ ={}
import kink
import yaml
from kink import di
from matplotlib import __getattr__

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
            print(f"Load config from {p}")
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
        working_dir = str(pathlib.Path(__file__).parent.parent)
        logger_dir = os.path.join(working_dir,logger_dir)
        if not os.path.isdir(logger_dir):
            os.makedirs(logger_dir)

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

def container(*args,**kwargs):
    fx=args
    def container_wrapper(cls):
        old_getattr=None
        if hasattr(cls,"__getattribute__"):
            old_getattr = getattr(cls,"__getattribute__")

        def __container__getattribute____(obj, item):
            ret= None
            if item[0:2]=="__" and item[-2]=="__":
                if old_getattr is not None:
                    return old_getattr(obj,item)
                else:
                    ret = cls.__dict__.get(item)

            else:
                ret = cls.__dict__.get(item)
            if ret is None:
                __annotations__ = cls.__dict__.get('__annotations__')
                if isinstance(__annotations__,dict):
                    ret =__annotations__.get(item)
            import inspect
            if inspect.isclass(ret):
                ret=container_wrapper(ret)
                return ret


            return ret
        setattr(cls,"__getattribute__",__container__getattribute____)
        return cls()

    return container_wrapper


def convert_to_dict(str_path:str,value):
    items = str_path.split('.')
    if items.__len__()==1:
        return {items[0]:value}
    else:
        return {items[0]: convert_to_dict(str_path[items[0].__len__()+1:],value)}

from copy import deepcopy

def __dict_of_dicts_merge__(x, y):
    z = {}
    if isinstance(x,dict) and isinstance(y,dict):
        overlapping_keys = x.keys() & y.keys()
        for key in overlapping_keys:
            z[key] = __dict_of_dicts_merge__(x[key], y[key])
        for key in x.keys() - overlapping_keys:
            z[key] = deepcopy(x[key])
        for key in y.keys() - overlapping_keys:
            z[key] = deepcopy(y[key])
        return z
    else:
        return y

def combine_agruments(data:dict):
    ret={}
    for x in sys.argv:
        if x.split('=').__len__()==2:
            k=x.split('=')[0]
            if x.split('=').__len__()==2:
                v=x.split('=')[1]
                c= convert_to_dict(k,v)
                ret=__dict_of_dicts_merge__(ret,c)
            else:
                c = convert_to_dict(k, None)
                ret = __dict_of_dicts_merge__(ret, c)
    ret = __dict_of_dicts_merge__(data,ret)
    return ret
def combine_os_variables(data:dict):
    import os
    ret={}
    for k,v in os.environ.items():
        if k.startswith('config.'):
            k=k['config.'.__len__():]
            c = convert_to_dict(k,v)
            ret=__dict_of_dicts_merge__(ret,c)
    ret = __dict_of_dicts_merge__(data,ret)
    return ret
def create_instance_from_moudle(module_name,class_name,force_reload=False):
    import importlib
    if force_reload:
        if module_name in list(sys.modules.keys()):
            importlib.reload(sys.modules[module_name])
    mdl = importlib.import_module(module_name)
    cls = getattr(mdl,class_name)
    return depen(cls)