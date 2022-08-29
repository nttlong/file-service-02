
"""
How to use?
Call set_root_dir for the first time to use. The path in argument of set_root_dir must be existing
Second call set_root_app_dir
Call get_logger to create new logger instance
"""
import logging

import os
__log__path__:str = None

import pathlib

"""
local varibale of log path
"""
__root_app_dir__:str = None
"""
local variable of root app dir
"""
def set_root_dir(absolute_dir_to_log:str):
    """
    Set root directory for logger
    :param absolute_dir_to_log: Absolute path point to root logs dir. Thy have to create before call method
    :return:
    """
    if not os.path.isdir(absolute_dir_to_log):
        raise Exception(f"{absolute_dir_to_log} was not found"
                        f"Thy have to create before call method")
    global __log__path__
    __log__path__= absolute_dir_to_log

def set_root_app_dir(path_to_root_app_dir:str):
    """
    Set root app dir every log will be generate inside
    :param path_to_root_app_dir:
    :return:
    """
    global __root_app_dir__
    __root_app_dir__ = path_to_root_app_dir

def get_logger(
        module_name,dir_to_log:str)-> logging.Logger:
    """
    Create new logger
    :param module_name: module to trace
    :param dir_to_log: relative or absolute path to sub dir with root was set by
                       call set_root_dir. relative path to dir will automatically create
                       if this argument is absolute path inside  set_root_app_dir
                       the log path will correspond with this argument value inside set_root_dir

    :return: A completely logging.Logger
    """
    if os.path.isfile(dir_to_log):
        dir_to_log = str(pathlib.Path(dir_to_log).parent)
    global __log__path__
    global  __root_app_dir__
    if __log__path__ is None: # check has set_root_dir call
        raise Exception(f"Thy must call {set_root_dir.__name__}  before call this")
    if __root_app_dir__ ==None: # check has set_root_app_dir call
        raise  Exception(f"Thy must call {set_root_app_dir.__name__} before call this")
    is_abs_path= os.path.abspath(dir_to_log)
    """
    dir_to_log is absolute
    """
    rel_path_to_log = dir_to_log
    """
    this variable will store relative path of log from __log__path__
    """
    if is_abs_path:
        rel_path_to_log = dir_to_log[__root_app_dir__.__len__():]
    full_path_to_log_dir = os.path.join(__log__path__,rel_path_to_log)
    if not os.path.isdir(full_path_to_log_dir):
        os.makedirs(full_path_to_log_dir)
    full_path_to_log =os.path.join(full_path_to_log_dir,module_name+".txt")
    ret = logging.getLogger(module_name)
    ret.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(levelname)s : %(name)s : %(message)s')
    file_handler = logging.FileHandler(full_path_to_log)
    file_handler.setFormatter(formatter)

    if (ret.hasHandlers()):
        ret.handlers.clear()
    ret.addHandler(file_handler)
    return ret

