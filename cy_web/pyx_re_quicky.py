import logging
import pathlib
import sys
from datetime import datetime
from typing import List

import fastapi

# from . import pyx_re_quicky_routers
import pyx_re_quicky_routers
from starlette.status import HTTP_401_UNAUTHORIZED

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException
from typing import Optional, Dict
from fastapi.security.oauth2 import OAuth2PasswordBearer
import jose
import jwt
import os
from fastapi.templating import Jinja2Templates


# wellknown_app: FastAPI = None
# __instance__ = None


def load_controller_from_file(file):
    if not os.path.isfile(file):
        print(f"{file} was not found")
        logging.Logger.error(f"{file} was not found")
    pass


class __Base__:
    def __init__(self):
        self.application_name = None
        self.main_module = None
        self.bind_ip = None
        self.bind_port = None
        self.host_url = None
        self.host_api_url = None
        self.host_schema = None
        self.__routers__ = None
        self.app: FastAPI = None
        self.controller_dirs: List[str] = []
        self.logs_dir: str = None
        self.logs: logging.Logger = None
        self.working_dir: str = None
        self.host_dir: str = None
        self.dev_mode: bool = False
        self.api_host_dir = "api"
        self.static_dir: str = None
        self.template_dir: str = None
        self.templates: Jinja2Templates = None
        self.url_get_token: str = None
        self.oauth2: OAuth2PasswordBearerAndCookie = None
        self.jwt_algorithm = None
        self.jwt_secret_key = None
        self.oauth2_type = None
        self.__on_auth__ = None



    def load_controller_from_dir(self, route_prefix: str = None, controller_dir: str = None):
        if controller_dir == None:
            return
        if controller_dir[0:2] == "./":
            controller_dir = os.path.join(self.working_dir, controller_dir[2:])
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
        for _file_ in files:
            self.load_conttroler_from_file(os.path.join(root_dir, _file_), route_prefix)
        for dir in dirs:
            self.load_controller_module_dir(os.path.join(root_dir, dir), route_prefix)

    def create_logs(self, logs_dir) -> logging.Logger:
        if not os.path.isdir(logs_dir):
            os.makedirs(logs_dir, exist_ok=True)

        _logs = logging.Logger("web")
        hdlr = logging.FileHandler(logs_dir + '/log{}.txt'.format(datetime.strftime(datetime.now(), '%Y%m%d%H%M%S_%f')))
        _logs.addHandler(hdlr)
        return _logs

    def load_controller_module_dir(self, module_dir, prefix: str = None) -> List[object]:

        # import pyx_re_quicky_routers
        module_path = os.path.join(module_dir, "__init__.py")
        _, _, files = list(os.walk(module_dir))[0]
        for _file_ in files:
            if os.path.splitext(_file_)[1] == ".py":
                full_file_path = os.path.join(module_dir, _file_)
                if os.path.isfile(full_file_path):
                    self.load_conttroler_from_file(full_file_path,prefix)
    def set_on_auth(self, fn):
        setattr(self.oauth2_type, "__call__", fn)

    def get_auth(self):
        return self.oauth2_type(
            token_url=self.url_get_token,
            jwt_algorithm=self.jwt_algorithm,
            jwt_secret_key=self.jwt_secret_key
        )

    def load_conttroler_from_file(self,full_file_path,prefix):
        if not os.path.isfile(full_file_path):
            return
        if os.path.splitext(full_file_path).__len__()!=2 and os.path.splitext(full_file_path)[1]!=".py":
            return

        import importlib.util
        import sys
        spec = importlib.util.spec_from_file_location(full_file_path, full_file_path)
        _mdl_ = importlib.util.module_from_spec(spec)
        # sys.modules[f"controllers.{controller_name}"] = _mdl_
        spec.loader.exec_module(_mdl_)
        for k, v in _mdl_.__dict__.items():
            if isinstance(v, pyx_re_quicky_routers.__hanlder__):
                _path = "/" + v.path
                if prefix is not None and prefix != "":
                    _path = "/" + prefix + _path
                if self.host_dir is not None:
                    _path = self.host_dir + _path

                if v.return_type is not None:
                    getattr(self.app, v.method)(_path, response_model=v.return_type)(v.handler)
                else:
                    getattr(self.app, v.method)(_path)(v.handler)


__cache_apps__ = {}

__instance__ = None
class WebApp(__Base__):


    def __init__(self,
                 app:FastAPI,
                 working_dir: str,
                 bind: str = "0.0.0.0:8011",
                 host_url: str = "http://localhost:8011",
                 logs_dir: str = "./logs",
                 controller_dirs: List[str] = [],
                 api_host_dir: str = "api",
                 static_dir: str = None,
                 dev_mode: bool = False,
                 template_dir: str = None,
                 url_get_token: str = "api/accounts/token",
                 jwt_algorithm: str = None,
                 jwt_secret_key: str = None
                 ):
        global __cache_apps__

        self.url_get_token = url_get_token
        self.jwt_algorithm = jwt_algorithm
        self.jwt_secret_key = jwt_secret_key
        self.template_dir = template_dir
        self.dev_mode = dev_mode
        self.api_host_dir = api_host_dir


        self.working_dir = working_dir
        self.static_dir = static_dir
        if self.static_dir is not None and self.static_dir[0:2] == "./":
            self.static_dir = os.path.join(self.working_dir, self.static_dir[2:])
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
        self.host_api_url = self.host_url + "/" + self.api_host_dir
        if remain.split('/')[0].split(':').__len__() == 2:
            self.host_port = int(remain.split('/')[0].split(':')[1])
            remain = remain[self.host_name.__len__() + str(self.host_port).__len__() + 1:]
        self.host_dir = None
        if remain != "":
            self.host_dir = remain

        self.app = app

        if self.static_dir is not None:
            from fastapi.staticfiles import StaticFiles
            if self.host_dir is not None and self.host_dir != "":
                self.app.mount(self.host_dir + "/static", StaticFiles(directory=self.static_dir), name="static")
            else:
                self.app.mount("/static", StaticFiles(directory=self.static_dir),
                               name="static")
        if self.template_dir is not None and self.template_dir[0:2] == "./":
            self.template_dir = os.path.join(self.working_dir, self.template_dir[2:])
        if self.template_dir is not None:
            self.templates = Jinja2Templates(directory=self.template_dir)

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
        if self.host_dir is not None and self.host_dir != "":
            self.url_get_token = self.host_dir + "/" + self.url_get_token

        self.oauth2_type = OAuth2PasswordBearerAndCookie



cy_request = fastapi.Request


class OAuth2PasswordBearerAndCookie(OAuth2PasswordBearer):
    def __init__(
            self,
            token_url: str,
            jwt_secret_key: str,
            jwt_algorithm: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            auto_error: bool = True

    ):
        if not scopes:
            scopes = {}
        super().__init__(
            tokenUrl=token_url,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
            scopes=scopes
        )
        self.jwt_secret_key = jwt_secret_key
        self.jwt_algorithm = jwt_algorithm
def add_controller(web_app,prefix_path: str, controller_dir):
    web_app.load_controller_from_dir(prefix_path, controller_dir)
def start_with_uvicorn(path:str,web_app:WebApp):
        import uvicorn

        if web_app.dev_mode:
            uvicorn.run(
                path,
                host=web_app.bind_ip,
                port=web_app.host_port,
                log_level="info",
                workers=8,
                lifespan='on',
                reload=web_app.dev_mode,
                reload_dirs=web_app.working_dir

            )
        else:
            uvicorn.run(
                path,
                host=web_app.bind_ip,
                port=web_app.host_port,
                log_level="info",
                workers=8,
                lifespan='on'

            )

def inject(cls):
    def call(instance,request:fastapi.Request):
        setattr(instance,"request",request)
        return instance
    setattr(cls,"__call__",cls)
    return fastapi.Depends(cls)