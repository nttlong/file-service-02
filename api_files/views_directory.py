from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import ReCompact.db_context
import ReCompact.dbm
import api_models.Model_Files
import ReCompact.HttpStream

async def source(request,app_name,full_path):
    print(f"load video {full_path}")
    db = ReCompact.db_context.get_db(app_name)
    upload_item = ReCompact.dbm.DbObjects.find_one_to_dict(
        db,
        api_models.Model_Files.DocUploadRegister,
        ReCompact.dbm.FILTER.FullFileName == full_path

    )
    fs= None
    server_file_name = upload_item["ServerFileName"]
    if upload_item.get("MainFileId",None):
        fs = ReCompact.db_context.get_mongodb_file_by_file_id(db,upload_item.get("MainFileId",None))
    else:
        fs = ReCompact.db_context.get_mongodb_file_by_file_name(db,server_file_name)
        if fs:
            ReCompact.dbm.DbObjects.update(
                db,
                data_item_type= api_models.Model_Files.DocUploadRegister,
                filter= ReCompact.dbm.FILTER._id == upload_item["_id"],
                updator= ReCompact.dbm.SET(
                    ReCompact.dbm.FIELDS.MainFileId==fs._id
                )
            )


    return  ReCompact.HttpStream.streaming_mongo_db_fs(request,fs)

# import asyncio
# from asyncio import coroutine
#
# @require_http_methods(["GET"])
# def source(request,app_name,full_path):
#     result = asyncio.get_event_loop().run_until_complete(__source__(request,app_name,full_path))
#     return result