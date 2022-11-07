import inspect
import logging
import os
import sys
from datetime import datetime
from typing import List, Union

import fastapi
import pydantic
from fastapi import FastAPI


wellknown_app: FastAPI = None
__instance__ = None


class __Base__:
    def __init__(self):
        self.bind_ip = None
        self.bind_port = None
        self.host_url = None
        self.host_schema = None
        self.__routers__ = None
        self.app: FastAPI = None
        self.controller_dirs: List[str] = []
        self.logs_dir: str = None
        self.logs: logging.Logger = None
        self.working_dir: str = None
        self.host_dir: str = None
        self.dev_mode:bool = False

    def start_with_uvicorn(self):
        import uvicorn
        uvicorn.run(
            f"{self.__module__}:wellknown_app",
            host=self.bind_ip,
            port=self.bind_port,
            log_level="info",
            reload= self.dev_mode
        )

    def load_controller_from_dir(self, controller_dir: str):
        if not os.path.isdir(controller_dir):
            print(f"{controller_dir} was not found")
            self.logs.error(msg=f"{controller_dir} was not found")
            return
        root_dir, dirs, files = list(os.walk(controller_dir))[0]
        import sys
        sys.path.append(self.working_dir)
        sys.path.append(root_dir)
        for x in dirs:
            sys.path.append(x)
        for dir in dirs:
            self.load_controller_module_dir(os.path.join(root_dir, dir), dir)
        print(root_dir, files, dirs)

    def create_logs(self, logs_dir) -> logging.Logger:
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)

        _logs = logging.Logger("web")
        hdlr = logging.FileHandler(logs_dir + '/log{}.txt'.format(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S_%f')))
        _logs.addHandler(hdlr)
        return _logs

    def load_controller_module_dir(self, module_dir, controller_name: str) -> List[object]:
        import pyx_re_quicky_routers
        module_path = os.path.join(module_dir, "__init__.py")
        ret = []
        if os.path.isfile(module_path):
            import importlib.util
            import sys
            spec = importlib.util.spec_from_file_location(f"controllers.{controller_name}", module_path)
            _mdl_ = importlib.util.module_from_spec(spec)
            sys.modules[f"controllers.{controller_name}"] = _mdl_
            spec.loader.exec_module(_mdl_)
            for k, v in _mdl_.__dict__.items():
                if isinstance(v, pyx_re_quicky_routers.__hanlder__):
                    _path = "/" + v.path
                    if self.host_dir is not None:
                        _path = self.host_dir + "/" + v.path
                    getattr(self.app, v.method)(_path)(v.handler)

    def load_controller_from_file(self, file):
        if not os.path.isfile(file):
            print(f"{file} was not found")
            logging.Logger.error(f"{file} was not found")
        pass


class WebApp(__Base__):
    def __new__(cls, *args, **kwargs):
        global __instance__
        if __instance__:
            return __instance__
        else:
            ret = __Base__()
            return cls.__init__(ret, *args, **kwargs)

    def __init__(self,
                 working_dir: str,
                 bind: str = "0.0.0.0:8011",
                 host_url: str = "http://localhost:8011",
                 logs_dir: str = "./logs",
                 controller_dirs: List[str] = [],
                 dev_mode:bool=False):
        global wellknown_app
        self.working_dir = working_dir
        self.logs_dir = logs_dir
        if self.logs_dir[0:2] == "./":
            self.logs_dir = os.path.join(self.working_dir, self.logs_dir[2:])
        self.logs: logging.Logger = self.create_logs(self.logs_dir)
        if bind.split(":").__len__() < 2:
            raise Exception(f"bind in {self.__module__}.{WebApp.__name__}.__init__ must look like 0.0.0.0:1234")
        self.bind_ip = bind.split(':')[0]
        self.bind_port = int(bind.split(':')[1])
        self.host_url = host_url
        self.host_schema = self.host_url.split(f"://")[0]
        remain = self.host_url[self.host_schema.__len__() + 3:]
        self.host_name = remain.split('/')[0].split(':')[0]
        self.host_port = None
        if remain.split('/')[0].split(':').__len__() == 2:
            self.host_port = int(remain.split('/')[0].split(':')[1])
            remain = remain[self.host_name.__len__() + str(self.host_port).__len__() + 1:]
        self.host_dir = None
        if remain != "":
            self.host_dir = remain

        wellknown_app = FastAPI()
        self.app = wellknown_app
        __instance__ = self
        self.controller_dirs = []
        for x in controller_dirs:
            if x[0:2] == "./":
                self.controller_dirs += [
                    os.path.join(self.working_dir, x[2:])
                ]
            else:
                self.controller_dirs += [x]
        for x in self.controller_dirs:
            self.load_controller_from_dir(x)

        return __instance__

    @property
    def app(self) -> FastAPI:
        return wellknown_app

    @classmethod
    def controller(cls):
        pass











from enum import Enum


class WebMethods(Enum):
    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "pacth"
    DELETE = "delete"


