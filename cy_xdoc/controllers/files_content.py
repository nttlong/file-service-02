import mimetypes

import fastapi
from fastapi import Header
from fastapi.responses import StreamingResponse
import cy_kit
import cy_web
import cy_xdoc
import cy_xdoc.services.files
import cy_xdoc.auths
import fasty.mongo_fs_http_streaming

@cy_web.hanlder(method="get",path="{app_name}/file/{directory:path}")
async def get_content_of_files(app_name: str, directory: str,request:fastapi.Request,token=fastapi.Depends(cy_xdoc.auths.Authenticate)):
    file_service = cy_kit.single(cy_xdoc.services.files.FileServices)
    upload_id= directory.split('/')[0]
    fs = file_service.get_main_file_of_upload(
        app_name=app_name,
        upload_id=upload_id
    )
    mime_type,_ = mimetypes.guess_type(directory)
    ret = await cy_web.cy_web_x.streaming_async(fs,request,mime_type)
    return ret

