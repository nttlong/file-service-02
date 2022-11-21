"""
Hiển thị nội dung OCR của file ảnh
"""
import fastapi
import cy_xdoc.auths
import cy_web
import cy_xdoc
import mimetypes
import cy_kit
import cy_xdoc.services.files
import cy_xdoc.services.file_storage
@cy_web.hanlder("get","{app_name}/file-ocr/{directory:path}")
async def files_contet_orc(app_name: str, directory: str, request: fastapi.Request,
                        token: str =fastapi.Depends(cy_xdoc.auths.Authenticate)):
    """
    Xem hoặc tải nội dung file
    :param app_name:
    :return:
    """

    mime_type, _ = mimetypes.guess_type(directory)

    file_service:cy_xdoc.services.files.FileServices = cy_kit.singleton(cy_xdoc.services.files.FileServices)
    file_srore_service = cy_kit.singleton(cy_xdoc.services.file_storage.FileStorageService)
    upload_id = directory.split('/')[0]
    upload = file_service.get_upload_register(app_name=app_name,upload_id=upload_id)
    if upload is None:
        return fastapi.Response(status_code=401)
    if upload.get("OCRFileId") is None:
        return fastapi.Response(status_code=401)
    fs = file_srore_service.get_file_by_id(
        app_name=app_name,
        id=upload.OCRFileId

    )

    if fs is None:
        return fastapi.Response(status_code=401)
    mime_type, _ = mimetypes.guess_type(directory)
    ret = await cy_web.cy_web_x.streaming_async(fs, request, mime_type)
    return ret
    # full_filename_without_ext = f"{str(pathlib.Path(directory).parent)}/{pathlib.Path(directory).stem}"
    # cntx = db_async.get_db_context(db_name)
    # file_info = await cntx.find_one_async(Files, Files.FullFileNameWithoutExtenstionLower == full_filename_without_ext.lower())
    # is_public= file_info.get(docs.Files.IsPublic.__name__,False)
    #
    # if not is_public:
    #     try:
    #         data_user = await fasty.JWT.get_current_user_async(app_name,token)
    #         if not data_user:
    #             if app_name=='admin':
    #                 url_login=fasty.config.app.root_url+'/login'
    #                 ret_url = urllib.parse.quote(request.url._url, safe='')
    #                 return RedirectResponse(url=url_login + f"?ret={ret_url}", status_code=status.HTTP_303_SEE_OTHER)
    #     except Exception as e:
    #         if app_name == 'admin':
    #             url_login = fasty.config.app.root_url + '/login'
    #             ret_url = urllib.parse.quote(request.url._url, safe='')
    #             return RedirectResponse(url=url_login + f"?ret={ret_url}", status_code=status.HTTP_303_SEE_OTHER)
    #
    #     app=await fasty.JWT.get_app_info_async(app_name)
    #     if app is None:
    #         return Response(status_code=401)
    #     else:
    #         if token is None or token=="":
    #             url_login=app[docs.sys_applications.LoginUrl.__name__]
    #             if url_login[0:2]=="~/":
    #                 url_login=fasty.config.app.root_url+'/'+url_login[2:]
    #
    #             ret_url=urllib.parse.quote(request.url._url, safe='')
    #             return RedirectResponse(url=url_login+f"?ret={ret_url}", status_code=status.HTTP_303_SEE_OTHER)
    #
    # fsg = await cntx.get_file_by_id(file_info[Files.OCRFileId.__name__])
    # content_type, _ = mimetypes.guess_type(directory)
    # res= await fasty.mongo_fs_http_streaming.streaming(fsg,request,content_type)
    # fsg.close()
    # res.headers.append("Cache-Control","max-age=86400")
    # return res
