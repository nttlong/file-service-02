"""
API liệt kê danh sách các file
"""
import humanize
import datetime
import uuid
import os
import mimetypes
import ReCompact.dbm
import fasty
from fastapi import FastAPI, Request, Response
import api_models.documents as docs
from ReCompact import db_async
import json
from db_connection import connection, default_db_name
from . import api_files_schema
from .models import AppInfo
from fastapi import Depends
from fastapi import Body
from .models import EditAppResutl, Error, ErrorType, AppInfo
from api_models.documents import Apps
from ReCompact.db_async import get_db_context, default_db_name, Error as Db_Error
import fasty.JWT
import fasty.JWT_Docs
from .models import register_new_upload_input
from .models import error
import ReCompact.db_async
from ReCompact.db_async import get_db_context
from pathlib import Path
import api_models.documents

docs = api_models.documents
"""
Các Mongodb Document Python Mappingh trong đây
"""
RegisterUploadInfo = register_new_upload_input.RegisterUploadInfo
"""
Ràng buộc thông tin đăng ký
"""
RegisterUploadInfoResult = register_new_upload_input.RegisterUploadInfoResult
"""
Cấu trúc trả về
"""


@fasty.api_post("/{app_name}/files/register", response_model=RegisterUploadInfoResult)
async def register_new_upload(app_name: str, Data: RegisterUploadInfo = Body(embed=True),
                              token: str = Depends(fasty.JWT.oauth2_scheme)):
    """

    :param app_name: Ứng dụng nào cần đăng ký Upload
    :param Data: Thông tin đăng ký Upload
    :param token:
    :return:
    """
    ret = RegisterUploadInfoResult()
    for k in list(Data.__dict__.keys()):
        if Data.__dict__.get(k, None) is None:
            ret.Error = error.Error()
            ret.Error.Code = ReCompact.db_async.ErrorType.DATA_REQUIRE.value
            ret.Error.Fields = [k]
            ret.Error.Message = f"'{k}' is require"
            return ret
    upload_id = str(uuid.uuid4())
    """
    Số upload
    """
    db_name = await fasty.JWT.get_db_name_async(app_name)
    if db_name is None:
        """
        Applcation không tìm thấy
        """
        return Response(status_code=403)

    db_context = get_db_context(db_name)
    _, file_extension = os.path.splitext(Data.FileName)
    mime_type, _ = mimetypes.guess_type(Data.FileName)
    reg_now = datetime.datetime.utcnow()
    chunk_size = Data.ChunkSizeInKB * 1024
    num_of_chunks, remain = divmod(Data.FileSize, chunk_size)
    if remain > 0:
        num_of_chunks += 1
    filename_only = Path(Data.FileName).stem.replace('#','_').replace('?','_').replace('/','_')
    ret_upload = await  db_context.insert_one_async(
        docs.Files,
        docs.Files._id == upload_id,
        docs.Files.FileName == Data.FileName,
        docs.Files.FileNameLower == Data.FileName.lower(),
        docs.Files.FileNameOnly == filename_only,
        docs.Files.FileExt == file_extension[1:],
        docs.Files.FullFileName == f"{upload_id}/{Data.FileName}",
        docs.Files.FullFileNameLower == f"{upload_id}/{Data.FileName.lower()}",
        docs.Files.FullFileNameWithoutExtenstion==f"{upload_id}/{filename_only}",
        docs.Files.FullFileNameWithoutExtenstionLower== f"{upload_id}/{filename_only}".lower(),
        docs.Files.ChunkSizeInKB == Data.ChunkSizeInKB,
        docs.Files.ChunkSizeInBytes == Data.ChunkSizeInKB * 1024,
        docs.Files.SizeInBytes == Data.FileSize,
        docs.Files.NumOfChunks == num_of_chunks,
        docs.Files.NumOfChunksCompleted == 0,
        docs.Files.SizeInHumanReadable == humanize.filesize.naturalsize(Data.FileSize),
        docs.Files.SizeUploaded == 0,
        docs.Files.ProcessHistories == [],
        docs.Files.ServerFileName==f"{upload_id}.{file_extension}",
        docs.Files.AvailableThumbSize == Data.ThumbConstraints,


        docs.Files.MimeType == mime_type,
        docs.Files.IsPublic == Data.IsPublic,
        docs.Files.Status == 0,
        docs.Files.RegisterOn == reg_now,
        docs.Files.RegisterOnDays == reg_now.day,
        docs.Files.RegisterOnHours == reg_now.hour,
        docs.Files.RegisterOnYears == reg_now.year,
        docs.Files.RegisterOnSeconds == reg_now.second,
        docs.Files.RegisterOnMinutes == reg_now.minute

    )
    ret.Data = register_new_upload_input.RegisterUploadResult()
    ret.Data.SizeInHumanReadable = ret_upload[docs.Files.SizeInHumanReadable.__name__]

    ret.Data.UrlThumb = f"{fasty.config.app.api_url}/thumb/{ret_upload[docs.Files._id.__name__]}/{ret_upload[docs.Files.FileNameLower.__name__]}.webp"
    ret.Data.RelUrlThumb = f"api/{app_name}/thumb/{ret_upload[docs.Files._id.__name__]}/{ret_upload[docs.Files.FileNameLower.__name__]}.webp"
    ret.Data.ServerFilePath=ret_upload[docs.Files.ServerFileName.__name__]
    ret.Data.UrlOfServerPath =f"{fasty.config.app.api_url}/{app_name}/file/{upload_id}/{ret_upload['FileName']}"
    ret.Data.RelUrlOfServerPath = f"api/{app_name}/file/{upload_id}/{ret_upload['FileName']}"
    ret.Data.UploadId = ret_upload["_id"]
    ret.Data.ServerFilePath=ret_upload[docs.Files.FullFileName.__name__]
    ret.Data.NumOfChunks = num_of_chunks
    ret.Data.ChunkSizeInBytes = chunk_size
    ret.Data.MimeType = mime_type
    ret.Data.FileSize=Data.FileSize
    return ret

