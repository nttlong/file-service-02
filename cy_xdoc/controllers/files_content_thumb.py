import os.path
import cy_kit
import cy_web
from fastapi import Request,Response
from fastapi.responses import FileResponse
from cy_xdoc.services.files import FileServices
import mimetypes
@cy_web.hanlder("get","{app_name}/thumb/{directory:path}")
async def get_thumb_of_files(app_name: str, directory: str, request: Request):
    """
    Xem hoặc tải nội dung file
    :param app_name:
    :return:
    """
    thumb_dir_cache = os.path.join(app_name,"thumbs")
    cache_thumb_path = cy_web.cache_content_check( thumb_dir_cache,directory.lower().replace("/","_"))
    if cache_thumb_path:
        return FileResponse(cache_thumb_path)
    file_service = cy_kit.single(FileServices)
    upload_id = directory.split('/')[0]
    fs = file_service.get_main_main_thumb_file(app_name,upload_id)
    if fs is None:
        return Response(
            status_code=401
        )
    content = fs.read()
    fs.seek(0)
    cy_web.cache_content(thumb_dir_cache, directory.replace('/', '_'), content)
    del content
    mime_type, _ = mimetypes.guess_type(directory)
    ret = await cy_web.cy_web_x.streaming_async(fs, request, mime_type)
    return ret
    # if cach_thumb_path is not None:
    #     from fastapi.responses import FileResponse
    #     res_file= FileResponse(cach_thumb_path)
    #     res_file.headers.append("Cache-Control", "max-age=86400")
    #     return res_file
    #
    # CHUNK_SIZE = 1024 * 1024
    # db_name = container.db_context.get_db_name(app_name)
    # cntx = db_async.get_db_context(db_name)
    # upload_id=directory.split('/')[0]
    # file_info = get_from_cahe(directory)
    # if file_info is None:
    #     file_info = await container.Services.files.get_item_by_upload_id_async(
    #         app_name=app_name,
    #         upload_id=upload_id
    #     )
    # if file_info:
    #     set_to_cache(directory, file_info)
    #     thumb_fs_id = file_info[api_models.documents.Files.ThumbFileId]
    #     if thumb_fs_id is None:
    #         return Response(status_code=401, content=f"'{directory}' in '{app_name} was not found")
    #     fsg = await container.Services.file_system.get_by_id_async(
    #         app_name=app_name,
    #         file_id = thumb_fs_id
    #     )
    #     # cntx.get_file_by_id(thumb_fs_id)
    #     content_type, _ = mimetypes.guess_type(directory)
    #     thumb_caching.sync(fsg.delegate._id,container.db_context.context(app_name).db.delegate,directory)
    #
    #     res= await fasty.mongo_fs_http_streaming.streaming(fsg,request,content_type)
    #     fsg.close()
    #     res.headers.append("Cache-Control", "max-age=86400")
    #     return res
    # else:
    #     return Response(status_code=401,content=f"'{directory}' in '{app_name} was not found")
