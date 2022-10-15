import pathlib
import sys
import threading

from fastapi.templating import Jinja2Templates
import os
__working_dir__ = str(pathlib.Path(__file__).parent.parent)
sys.path.append(__working_dir__)
from kink import di
import enigma.config
import enigma.loggers
app_config=enigma.config.AppConfig()
"""
All config access here. in order to use the app_config you must start app with config_path arg
"""
app_logger = enigma.loggers.ELogger()

get_logger = enigma.loggers.get_logger
def get_root_url()->str:
    ret= f"{enigma.app_config.get_config('host_schema')}://{enigma.app_config.get_config('host_name')}"
    if enigma.app_config.get_config('host_port') is not None:
        ret=f"{ret}:{enigma.app_config.get_config('host_port')}"
    return ret
def get_host_schema()->str:
    return enigma.app_config.get_config('host_schema')
def get_root_api_url()->str:
    return f"{get_root_url()}/{enigma.app_config.get_config('api_host_dir')}"
templates = Jinja2Templates(directory=app_config.get_config('jinja_templates_dir'))

__static_dir__=None
__lock__= threading.Lock()
def get_static_dir():
    global __static_dir__
    global  __lock__
    if __static_dir__ is None:
        __lock__.acquire()
        try:
            __static_dir__ = enigma.app_config.get_config('static_dir')
            __wd__ = str(pathlib.Path(__file__).parent.parent)
            if __static_dir__[0:2] == "./":
                __static_dir__ = __static_dir__[2:]
                __static_dir__ = os.path.join(__wd__, __static_dir__).replace('/', os.sep)
        except Exception as e:
            raise e
        finally:
            __lock__.release()
    return __static_dir__

__tmp_upload_dir__ = None

def get_temp_upload_dir(app_name):
    global __tmp_upload_dir__
    global __lock__
    if __tmp_upload_dir__ is None:
        __lock__.acquire()
        try:
            __tmp_upload_dir__ = enigma.app_config.get_config('tmp_upload_dir')
            if __tmp_upload_dir__[0:2] == "./":
                __tmp_upload_dir__ = __tmp_upload_dir__[2:]
                wd = str(pathlib.Path(__file__).parent.parent)
                __tmp_upload_dir__ = os.path.join(
                    wd, __tmp_upload_dir__
                ).replace('/', os.sep)
                if not os.path.isdir(__tmp_upload_dir__):
                    os.makedirs(__tmp_upload_dir__)
        except Exception as e:
            raise e
        finally:
            __lock__.release()
    ret= os.path.join(__tmp_upload_dir__,app_name)
    if not os.path.isdir(ret):
        os.makedirs(ret)
    return ret