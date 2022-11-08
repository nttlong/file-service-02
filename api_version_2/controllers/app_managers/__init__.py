import typing

import fastapi
import pydantic
from fastapi import File, UploadFile
import cy_web

class Application:
    Name:typing.Optional[str]
def get_app(app_name:str):
    return f"{app_name}_xxx"

# @cy_web.post("{app_name}/images")
# def register(app_name:str,items:typing.List[str],apps:typing.List[Application],appx=fastapi.Depends(get_app) )->Application:
#     return Application(
#
#     )
from  typing import List
@cy_web.form_post("{app_name}/login")

def login(app_name:str,username:str,password:str,my_files:List[UploadFile]=File(),  appx=fastapi.Depends(get_app) )->Application:
    """
    Test
    """
    return Application(
        Name=appx

    )