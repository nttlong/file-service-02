import typing

import fastapi
import pydantic
from fastapi import File, UploadFile
import cy_web
def test(app_name:str):
    return "XXX"
@cy_web.post("{app_name}app/list")
async def get_list(app_name, token: str = fastapi.Depends(cy_web.auth())):
    return [app_name,token]