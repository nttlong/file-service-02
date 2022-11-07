import typing

import fastapi
import pydantic
from fastapi import File, UploadFile
import re_quicky

class Application:
    Name:typing.Optional[str]
def get_app(app_name:str):
    return f"{app_name}_xxx"

# @re_quicky.post("{app_name}/images")
# def register(app_name:str,items:typing.List[str],apps:typing.List[Application],appx=fastapi.Depends(get_app) )->Application:
#     return Application(
#
#     )
from  typing import List
@re_quicky.form_post("{app_name}/login")
def login(app_name:str,username:str,password:str,my_files:List[UploadFile]=File(),  appx=fastapi.Depends(get_app) )->Application:
    return Application(
        Name=appx

    )