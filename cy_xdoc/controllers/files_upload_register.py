# """
# API liệt kê danh sách các file
# """
# import humanize
# import datetime
# import uuid
# import os
# import mimetypes
# import ReCompact.dbm
#
# import enig_frames.containers
# from fastapi import Response
# import api_models.documents as docs
# from ReCompact import db_async
# from fastapi import Depends
# from fastapi import Body
# import fasty.JWT
# import fasty.JWT_Docs
# from .models import register_new_upload_input
# from .models import error
# import ReCompact.db_async
# from ReCompact.db_async import get_db_context
# from pathlib import Path
# import api_models.documents
#
# docs = api_models.documents
# """
# Các Mongodb Document Python Mappingh trong đây
# """
# RegisterUploadInfo = register_new_upload_input.RegisterUploadInfo
# """
# Ràng buộc thông tin đăng ký
# """
# RegisterUploadInfoResult = register_new_upload_input.RegisterUploadInfoResult
# """
# Cấu trúc trả về
# """
import fastapi
import cy_web
import cy_kit
import cy_xdoc.auths
from cy_xdoc.services.files import FileServices
from cy_xdoc.controllers.models.files_register import RegisterUploadInfo,RegisterUploadInfoResult
@cy_web.hanlder("post","{app_name}/files/register")
async def register_new_upload(app_name: str, Data: RegisterUploadInfo,token = fastapi.Depends(cy_xdoc.auths.Authenticate))->RegisterUploadInfoResult:
    """

    :param app_name: Ứng dụng nào cần đăng ký Upload
    :param Data: Thông tin đăng ký Upload
    :param token:
    :return:
    """
    file_service = cy_kit.single(FileServices)
    ret = file_service.add_new_upload_info(
        app_name=app_name,
        chunk_size= Data.ChunkSizeInKB * 1024,
        file_size= Data.FileSize,
        client_file_name= Data.FileName,
        is_public= Data.IsPublic,
        thumbs_support= Data.ThumbConstraints,
        web_host_root_url= cy_web.get_host_url()
    )
    return RegisterUploadInfoResult(Data = ret.to_pydantic())



