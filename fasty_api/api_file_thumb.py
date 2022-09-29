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
from db_connection import connection, default_db_name
from . import api_files_schema
from api_models.documents import Files
from ReCompact import db_async
from fastapi.responses import StreamingResponse
import os
from fasty import mime_data
import mimetypes
import fasty.mongo_fs_http_streaming
fasty.app.get("test/ping-server")
async  def test():
    return dict(Ok="OK")
@fasty.api_get("/{app_name}/thumb/{directory:path}")
async def get_thumb_of_files(app_name: str, directory: str, request: Request):
    """
    Xem hoặc tải nội dung file
    :param app_name:
    :return:
    """
    CHUNK_SIZE = 1024 * 1024
    cntx = db_async.get_db_context(app_name)
    upload_id=directory.split('/')[0]
    file_info = await cntx.find_one_async(Files, Files._id == upload_id)
    if file_info:
        thumb_fs_id = file_info.get(Files.ThumbFileId.__name__,None)
        fsg = await cntx.get_file_by_id(thumb_fs_id)
        content_type, _ = mimetypes.guess_type(directory)
        res= await fasty.mongo_fs_http_streaming.streaming(fsg,request,content_type)
        fsg.close()
        res.headers.append("Cache-Control", "max-age=86400")
        return res
    else:
        return Response(status_code=401,content=f"'{directory}' in '{app_name} was not found")
