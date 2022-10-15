"""
Tải nộ udng ảnh Thumb
"""
import motor

import ReCompact.dbm
import fasty
from fastapi import FastAPI, Request, Header, Response
import api_models.documents as docs
from ReCompact import db_async
import json

from . import api_files_schema
from api_models.documents import Files,Fs_File
from ReCompact import db_async
from fastapi.responses import StreamingResponse
import os
from fasty import mime_data
import mimetypes
import fasty.mongo_fs_http_streaming
import threading

__cache__ ={}
__lock__ = threading.Lock()
from fasty_api import thumb_caching
def get_from_cahe(id:str)->dict:
    global __cache__
    return __cache__.get(id.lower())
def set_to_cache(id,data):

    global __cache__
    try:
        __lock__.acquire()
        __cache__[id.lower()]=data
    finally:
        __lock__.release()
@fasty.api_get("/{app_name}/thumbs/{directory:path}")
async def get_thumb_of_files(app_name: str, directory: str, request: Request):
    """
    Xem hoặc tải nội dung file
    :param app_name:
    :return:
    """
    cach_thumb_path = thumb_caching.check(directory.replace('/','__'))
    if cach_thumb_path is not None:
        from fastapi.responses import FileResponse
        res_fs = FileResponse(cach_thumb_path)
        res_fs.headers.append("Cache-Control", "max-age=86400")
        return res_fs

    cntx = db_async.get_db_context(app_name)
    fs = await cntx.find_one_async(
        Fs_File,
        filter= Fs_File.rel_file_path==f"thumbs/{directory.lower()}"


    )
    if fs is None:
        return Response(status_code=401, content=f"'{directory}' in '{app_name} was not found")
    fsg = await cntx.get_file_by_id(fs.get("_id"))
    thumb_caching.sync(fsg.delegate._id, db_async.get_db_context(app_name).db.delegate, directory.replace('/','__'))
    content_type,_=mimetypes.guess_type(directory)
    res = await fasty.mongo_fs_http_streaming.streaming(fsg, request, content_type)
    res.headers.append("Cache-Control", "max-age=86400")
    return res

    #
    # CHUNK_SIZE = 1024 * 1024
    # cntx = db_async.get_db_context(app_name)
    # upload_id=directory.split('/')[0]
    # file_info = get_from_cahe(directory)
    # if file_info is None:
    #     file_info = await cntx.find_one_async(Files, Files._id == upload_id)
    # if file_info:
    #     set_to_cache(directory, file_info)
    #     thumb_fs_id = file_info.get(Files.ThumbFileId.__name__,None)
    #     fsg = await cntx.get_file_by_id(thumb_fs_id)
    #     content_type, _ = mimetypes.guess_type(directory)
    #     thumb_caching.sync(fsg.delegate._id,db_async.get_db_context(app_name).db.delegate,directory)
    #
    #     res= await fasty.mongo_fs_http_streaming.streaming(fsg,request,content_type)
    #     fsg.close()
    #     res.headers.append("Cache-Control", "max-age=86400")
    #     return res
    # else:
    #     return Response(status_code=401,content=f"'{directory}' in '{app_name} was not found")
