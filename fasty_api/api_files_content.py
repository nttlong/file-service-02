"""
API liệt kê danh sách các file
"""
import threading

import motor

import ReCompact.dbm
import fasty
from fastapi import FastAPI, Request, Header, Response
import api_models.documents as docs
from ReCompact import db_async
import json
from db_connection import connection, default_db_name
from . import api_files_schema
from api_models.documents import Files
from ReCompact import db_async
from fastapi.responses import StreamingResponse
import os
from fasty import mime_data
import mimetypes
import fasty.mongo_fs_http_streaming
from fastapi import Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
import urllib
import fasty.JWT
import threading
import fasty_api.image_caching
__cache__ ={}
__lock__ = threading.Lock()
def get_from_cahe(id:str)->dict:
    global __cache__
    return __cache__.get(id.lower())
def set_to_cache(id,data):
    global __cache__
    __cache__[id.lower()]=data
def clear_cache():
    global __lock__
    global __cache__
    __cache__={}

@fasty.api_get("/{app_name}/file/{directory:path}")
async def get_content_of_files(app_name: str, directory: str, request: Request,
                               token: str = Depends(fasty.JWT.get_oauth2_scheme_anonymous())):
    try:
        """
        Xem hoặc tải nội dung file
        :param app_name:
        :return:
        """
        mime_type,_ = mimetypes.guess_type(directory)
        if "image/" in mime_type:
            file_path=fasty_api.image_caching.check(directory)
            if file_path is not None:
                from fastapi.responses import FileResponse
                res_file = FileResponse(file_path)
                res_file.headers.append("Cache-Control","max-age=86400")
                return res_file

        CHUNK_SIZE = 1024 * 1024
        db_name = await fasty.JWT.get_db_name_async(app_name)
        if db_name is None:
            return Response(status_code=401)

        cntx = db_async.get_db_context(db_name)
        from re import compile
        file_info = get_from_cahe(directory)
        if not file_info:
            file_info = await cntx.find_one_async(Files, Files.FullFileNameLower == compile('^' + directory.lower() + '$'))

        if not file_info:
            file_info = await cntx.find_one_async(Files, Files.FullFileName == directory.lower())
            if file_info:
                set_to_cache(directory,file_info)
                await cntx.update_one_async(
                    docs.Files,
                    docs.Files._id == file_info["_id"],
                    docs.Files.FullFileNameLower == directory.lower()
                )
            else:
                file_info = await cntx.find_one_async(Files, Files.FileNameLower == directory.lower())
                if file_info:
                    set_to_cache(directory,file_info)
                    await cntx.update_one_async(
                        docs.Files,
                        docs.Files._id == file_info["_id"],
                        docs.Files.FullFileNameLower == directory.lower()
                    )

        if file_info:
            if not file_info.get(Files.MainFileId.__name__):
                import ReCompact.db_context
                fix_fs = ReCompact.db_context.get_mongodb_file_by_file_name(
                    cntx.db.delegate,
                    file_info[docs.Files.ServerFileName.__name__]
                )
                await cntx.update_one_async(
                    docs.Files,
                    docs.Files._id == file_info["_id"],
                    docs.Files.MainFileId == fix_fs._id
                )
                file_info[Files.MainFileId.__name__] = fix_fs._id
                set_to_cache(directory, file_info)
            fs_id = file_info[Files.MainFileId.__name__]
        else:
            upload_id = directory.split('/')[0]
            file_info = await cntx.find_one_async(Files, Files._id == upload_id)
            if not file_info:
                return Response(status_code=401)
            else:
                set_to_cache(directory, file_info)

        is_public = file_info.get(docs.Files.IsPublic.__name__, False)
        if not is_public:
            try:
                data_user = await fasty.JWT.get_current_user_async(app_name, token)
                if not data_user:
                    if app_name == 'admin':
                        url_login = fasty.config.app.root_url + '/login'
                        ret_url = urllib.parse.quote(request.url._url, safe='')
                        return RedirectResponse(url=url_login + f"?ret={ret_url}",
                                                status_code=status.HTTP_303_SEE_OTHER)
            except Exception as e:
                if app_name == 'admin':
                    url_login = fasty.config.app.root_url + '/login'
                    ret_url = urllib.parse.quote(request.url._url, safe='')
                    return RedirectResponse(url=url_login + f"?ret={ret_url}", status_code=status.HTTP_303_SEE_OTHER)

            app = await fasty.JWT.get_app_info_async(app_name)
            if app is None:
                return Response(status_code=401)
            else:
                if token is None or token == "":
                    url_login = app[docs.sys_applications.LoginUrl.__name__]
                    if url_login[0:2] == "~/":
                        url_login = fasty.config.app.root_url + '/' + url_login[2:]

                    ret_url = urllib.parse.quote(request.url._url, safe='')
                    return RedirectResponse(url=url_login + f"?ret={ret_url}", status_code=status.HTTP_303_SEE_OTHER)
        main_file_id = file_info.get(Files.MainFileId.__name__)

        fsg = await cntx.get_file_by_id(file_info[Files.MainFileId.__name__])
        if "image/" in mime_type:
            fasty_api.image_caching.sync(fsg.delegate._id, db_async.get_db_context(app_name).db.delegate, directory)
        if fsg is None:
            return Response(status_code=401)
        content_type, _ = mimetypes.guess_type(directory)

        if content_type is None:
            content_type='application/octet-stream'

        res = await fasty.mongo_fs_http_streaming.streaming(fsg, request, content_type)
        fsg.close()
        res.headers.append("Cache-Control","max-age=86400")
        return res
    except Exception as e:
        raise e
