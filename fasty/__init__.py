"""
The pakage support for FastAPI
"""

# from fastapi.middleware.cors import CORSMiddleware
import mimetypes

import enig_frames.containers

from . import mime_data

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import traceback
import pathlib
import ReCompact.db_async
from fastapi import logger
import os
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response
__api_host_dir__ =enig_frames.containers.Container.config.config.api_host_dir
if __api_host_dir__[0] != "/":
    __api_host_dir__ = '/' + __api_host_dir__
# path_to_yam_db =os.path.join(str(pathlib.Path(__file__).parent.parent.absolute()),"database.yaml")

# ReCompact.db_async.load_config(path_to_yam_db)
from . import start
from fastapi import FastAPI
import enig_frames.containers
import ReCompact.db_async
import sys
app = None
container = enig_frames.containers.Container
logger = container.loggers.get_logger(__name__)
def install_fastapi_app(module_name:str):

    from fastapi.middleware.cors import CORSMiddleware
    global app
    global config
    app = FastAPI()
    setattr(sys.modules[module_name], "app", app)
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.middleware(container.config.config.host_schema)(catch_exceptions_middleware)
    app.mount("/static", StaticFiles(directory=container.Services.applications.configuration.static_dir), name="static")


    return app

def page_get(url_path:str,response_class=HTMLResponse):
    global app
    fn = app.get(url_path, response_class=response_class)
    return fn


def api_get(url_path:str,response_class=None):
    global app
    global __api_host_dir__
    if __api_host_dir__ is not None and __api_host_dir__!="":
        if response_class is None:

            logger.info("------------------handler ------------")
            logger.info(__api_host_dir__+ url_path)
            logger.info("------------------handler ------------")
            fn = app.get(__api_host_dir__ + url_path)
            return fn
        else:
            logger.info("------------------handler ------------")
            logger.info(__api_host_dir__ + url_path)
            logger.info("------------------handler ------------")
            fn = app.get(__api_host_dir__+url_path,response_class=response_class)
            return fn
    else:
        if response_class is None:
            logger.info("------------------handler ------------")
            logger.info(url_path)
            logger.info("------------------handler ------------")
            fn = app.get(url_path)
            return fn
        else:
            logger.info("------------------handler ------------")
            logger.info(url_path)
            logger.info("------------------handler ------------")
            fn=app.get(url_path,response_class=response_class)
            return  fn

def api_post(url_path:str,response_class=None,response_model=None):
    global app
    global __api_host_dir__
    if __api_host_dir__ is not None and __api_host_dir__ != "":

        if response_class is None:
            if response_model is None:
                fn = app.post(__api_host_dir__+url_path)
                return fn
            else:
                fn = app.post(__api_host_dir__ + url_path,response_model=response_model)
                return fn
        else:
            fn = app.post(__api_host_dir__ + url_path,response_class=response_class)
            return fn
    else:
        if response_class is None:
            fn = app.post(url_path)
            return fn
        else:
            fn=app.post(url_path,response_class=response_class)
            return  fn
async def catch_exceptions_middleware(request: Request, call_next):
   try:
       res = await call_next(request)
       if request.url.path.endswith('.js') and '/static/' in request.url.path:
           t,_ =mimetypes.guess_type(request.url.path)
           res.headers['content-type'] = t

       return res
   except Exception as e:
       import fasty.start
       logger.exception(e)
       return Response("Internal server error", status_code=500)



