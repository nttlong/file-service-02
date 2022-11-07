import pathlib
import sys
import os
"""
api_version_2/re_quicky/source/build/lib.linux-x86_64-3.8/pyx_re_quicky.cpython-38-x86_64-linux-gnu.so
"""
# if sys.platform != "linux":
#     raise Exception(f"The module is not available for {sys.platform}")
# else:
#     sys.path.append(
#         os.path.join(pathlib.Path(__file__).parent.__str__(), "source","build","lib.linux-x86_64-3.8")
#     )


from typing import List
def create_app(
                 working_dir: str,
                 bind: str = "0.0.0.0:8011",
                 host_url: str = "http://localhost:8011",
                 logs_dir: str = "./logs",
                 controller_dirs: List[str] = [],
                 dev_mode:bool=False
):
    global __app__
    from . import pyx_re_quicky
    # from pyx_re_quicky import WebApp
    __app__ = pyx_re_quicky.WebApp(
        working_dir=working_dir,
        bind=bind,
        host_url=host_url,
        logs_dir=logs_dir,
        controller_dirs=controller_dirs,
        dev_mode =dev_mode

    )
    return __app__
def uvicon_start():
    global __app__
    __app__.start_with_uvicorn()

def handle_get(path:str):
    from . import pyx_re_quicky_routers
    # import pyx_re_quicky_routers
    return getattr(pyx_re_quicky_routers,"web_handler")(path,method="get")

def check_is_need_pydantic(cls:type)->bool:
    import pyx_re_quicky_routers
    return getattr(pyx_re_quicky_routers, "check_is_need_pydantic")(type)
