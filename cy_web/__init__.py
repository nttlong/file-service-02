import pathlib
import sys
import os
import fastapi.templating
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response

"""
api_version_2/cy_web/source/build/lib.linux-x86_64-3.8/pyx_re_quicky.cpython-38-x86_64-linux-gnu.so
"""
if sys.platform != "linux":
    raise Exception(f"The module is not available for {sys.platform}")
else:
    sys.path.append(
        os.path.join(pathlib.Path(__file__).parent.__str__(), "build", "lib.linux-x86_64-3.8", "cy_web")
    )
__is_build__ = False

from typing import List


def create_app(working_dir: str,
               bind: str = "0.0.0.0:8011",
               host_url: str = "http://localhost:8011",
               logs_dir: str = "./logs",
               controller_dirs: List[str] = [],
               static_dir=None,
               dev_mode: bool = False,
               template_dir: str = None,
               url_get_token: str = "api/accounts/token",
               jwt_secret_key: str = None,
               jwt_algorithm: str = None):
    global __app__
    global __is_build__
    if not __is_build__:
        import pyx_re_quicky

    else:
        from . import pyx_re_quicky
    # from pyx_re_quicky import WebApp
    __app__ = pyx_re_quicky.WebApp(
        working_dir=working_dir,
        bind=bind,
        host_url=host_url,
        logs_dir=logs_dir,
        controller_dirs=controller_dirs,
        dev_mode=dev_mode,
        static_dir=static_dir,
        template_dir=template_dir,
        jwt_secret_key=jwt_secret_key,
        jwt_algorithm=jwt_algorithm,
        url_get_token=url_get_token

    )
    return __app__


def add_controller(prefix_path:str,controller_dir):
    global __app__
    __app__.load_controller_from_dir(prefix_path,controller_dir)
    print(__app__)

def init_SPA(web_app):
    url = "/"
    if web_app.host_url is not None and web_app.host_dir != "":
        url = web_app.host_dir

    @web_app.app.get(url, response_class=HTMLResponse)
    def home_page():
        data = dict(
            host_url=web_app.host_url,
            full_app_url=web_app.host_url + "/",
            host_dir=web_app.host_dir,
            host_api_url=web_app.host_api_url
        )

        return web_app.templates.TemplateResponse("index.html", {"request": data})

    def get_dir(directory):
        return directory

    @web_app.app.get(url + "/{directory:path}", response_class=HTMLResponse)
    async def page_single(directory: str = fastapi.Depends(get_dir)):

        directory = directory.split('?')[0]
        check_dir_path = os.path.join(web_app.static_dir, "views", directory.replace('/', os.sep))

        if not os.path.exists(check_dir_path):
            return Response(status_code=401)

        # host_services = enig.create_instance(enig_frames.services.hosts.Hosts)
        data = dict(
            host_url=web_app.host_url,
            full_app_url=web_app.host_url + "/",
            host_dir=web_app.host_dir,
            host_api_url=web_app.host_api_url
        )

        return web_app.templates.TemplateResponse("index.html", {"request": data})


def uvicon_start():
    global __app__
    init_SPA(__app__)
    __app__.start_with_uvicorn()


def get(path: str):
    global __is_build__
    if not __is_build__:
        import pyx_re_quicky_routers
    else:
        from . import pyx_re_quicky_routers
    # import pyx_re_quicky_routers
    return getattr(pyx_re_quicky_routers, "web_handler")(path, method="get")


def post(path: str):
    global __is_build__
    if not __is_build__:
        import pyx_re_quicky_routers
    else:
        from . import pyx_re_quicky_routers
    # import pyx_re_quicky_routers
    return getattr(pyx_re_quicky_routers, "web_handler")(path, method="post")


def form_post(path: str):
    global __is_build__
    if not __is_build__:
        import pyx_re_quicky_routers
    else:
        from . import pyx_re_quicky_routers
    # import pyx_re_quicky_routers
    return getattr(pyx_re_quicky_routers, "web_handler")(path, method="form")


def check_is_need_pydantic(cls: type) -> bool:
    global __is_build__
    if not __is_build__:
        import pyx_re_quicky_routers
    else:
        from . import pyx_re_quicky_routers
    return getattr(pyx_re_quicky_routers, "check_is_need_pydantic")(type)
