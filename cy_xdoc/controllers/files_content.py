import mimetypes

import fastapi
from fastapi.responses import Response
import cy_kit
import cy_web
import cy_xdoc
import cy_xdoc.services.files
import cy_xdoc.auths

from  cyx.common.base import config
@cy_web.hanlder(method="get", path="{app_name}/file/{directory:path}")
async def get_content_of_files(app_name: str, directory: str, request: fastapi.Request):
    mime_type, _ = mimetypes.guess_type(directory)
    if mime_type.startswith('image/'):
        file_cache = cy_web.cache_content_check(app_name, directory.replace('/', '_'))
        if file_cache:
            return fastapi.responses.FileResponse(path=file_cache)

    file_service = cy_kit.singleton(cy_xdoc.services.files.FileServices)
    upload_id = directory.split('/')[0]
    upload = file_service.get_upload_register(app_name,upload_id)
    runtime_file_reader = None
    if upload and upload.FileModuleController:
        try:
            runtime_file_reader = cy_kit.singleton_from_path(upload.FileModuleController)
        except ModuleNotFoundError as e:
            runtime_file_reader = None

    fs = file_service.get_main_file_of_upload_by_rel_file_path(
        app_name=app_name,
        rel_file_path=directory,
        runtime_file_reader =runtime_file_reader
    )

    if fs is None:

        fs = file_service.get_main_file_of_upload(
            app_name=app_name,
            upload_id=upload_id
        )

    if fs is None:
        return Response(status_code= 401)
    if mime_type.startswith('image/'):
        content = fs.read(fs.get_size())
        fs.seek(0)
        cy_web.cache_content(app_name, directory.replace('/', '_'), content)
        del content
    mime_type, _ = mimetypes.guess_type(directory)
    if hasattr(fs,"cursor_len"):
        setattr(fs,"cursor_len",config.content_segment_len)
    ret = await cy_web.cy_web_x.streaming_async(
        fs, request, mime_type,streaming_buffering=1024*4*3*8
    )
    return ret
