"""
Hiển thị nội dung OCR của file ảnh
"""
import pathlib

import motor

import ReCompact.dbm
import fasty
from fastapi import FastAPI, Request, Header, Response
import api_models.documents as docs
from ReCompact import db_async
import json

from . import api_files_schema
from api_models.documents import Files
from ReCompact import db_async
from fastapi.responses import StreamingResponse
import os
import mimetypes
import fasty.mongo_fs_http_streaming
from  fastapi import Depends,status
from fastapi.responses import RedirectResponse, HTMLResponse
import urllib
import fasty.JWT
@fasty.api_get("/{app_name}/file-ocr/{directory:path}")
async def get_ocr_content_of_files(app_name: str, directory: str, request: Request,
                        token: str = Depends(fasty.JWT.get_oauth2_scheme_anonymous())):
    """
    Xem hoặc tải nội dung file
    :param app_name:
    :return:
    """
    CHUNK_SIZE = 1024 * 1024
    db_name = await fasty.JWT.get_db_name_async(app_name)
    if db_name is None:
        return Response(status_code=401)
    full_filename_without_ext = f"{str(pathlib.Path(directory).parent)}/{pathlib.Path(directory).stem}"
    cntx = db_async.get_db_context(db_name)
    file_info = await cntx.find_one_async(Files, Files.FullFileNameWithoutExtenstionLower == full_filename_without_ext.lower())
    is_public= file_info.get(docs.Files.IsPublic.__name__,False)

    if not is_public:
        try:
            data_user = await fasty.JWT.get_current_user_async(app_name,token)
            if not data_user:
                if app_name=='admin':
                    url_login=fasty.config.app.root_url+'/login'
                    ret_url = urllib.parse.quote(request.url._url, safe='')
                    return RedirectResponse(url=url_login + f"?ret={ret_url}", status_code=status.HTTP_303_SEE_OTHER)
        except Exception as e:
            if app_name == 'admin':
                url_login = fasty.config.app.root_url + '/login'
                ret_url = urllib.parse.quote(request.url._url, safe='')
                return RedirectResponse(url=url_login + f"?ret={ret_url}", status_code=status.HTTP_303_SEE_OTHER)

        app=await fasty.JWT.get_app_info_async(app_name)
        if app is None:
            return Response(status_code=401)
        else:
            if token is None or token=="":
                url_login=app[docs.sys_applications.LoginUrl.__name__]
                if url_login[0:2]=="~/":
                    url_login=fasty.config.app.root_url+'/'+url_login[2:]

                ret_url=urllib.parse.quote(request.url._url, safe='')
                return RedirectResponse(url=url_login+f"?ret={ret_url}", status_code=status.HTTP_303_SEE_OTHER)

    fsg = await cntx.get_file_by_id(file_info[Files.OCRFileId.__name__])
    content_type, _ = mimetypes.guess_type(directory)
    res= await fasty.mongo_fs_http_streaming.streaming(fsg,request,content_type)
    fsg.close()
    res.headers.append("Cache-Control","max-age=86400")
    return res
