import cy_web
from cy_xdoc.auths import Authenticate
from fastapi import File,Depends,UploadFile
import typing
@cy_web.hanlder("post", "/{app_name}/files/upload")
def files_upload(app_name: str, UploadId:str,Index:int,FilePart: typing.List[UploadFile],token= Depends(Authenticate)):
    pass