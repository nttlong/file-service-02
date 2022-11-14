import sys

import cy_web
from cy_xdoc.controllers.models.apps import AppInfo
from cy_xdoc.auths import Authenticate
import fastapi.params
from typing import List



@cy_web.hanlder(method="post", path="{app_name}/apps")
def get_list_of_apps(app_name:str,token = fastapi.Depends(Authenticate))->List[AppInfo]:
    return []
