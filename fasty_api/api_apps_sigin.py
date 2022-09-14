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
import mimetypes
import fasty.mongo_fs_http_streaming
from  fastapi import Depends,status,Request,Response
from fastapi.responses import RedirectResponse, HTMLResponse
import urllib
import fasty.JWT
import fasty.JWT_Docs
from ReCompact.db_async import get_db_context,default_db_name
from fastapi_jwt_auth import AuthJWT
@fasty.api_get("/sso/signin/{SSOID}")
async def do_sign_in(SSOID:str,request:Request, Authorize: AuthJWT = Depends()):
    """
    Đăng nhập vào dịch vụ bằng SSOID.
    Khi 1 web site remote muốn truy cập vào dịch vụ bằng trình duyệt,
    nhưng lại không thể gởi access token qua header hoặc request params.
    (Ví dụ như xem nôi dung file bằng url của dịch vụ ngay tại site remote)
    Thì web site remote phải redirect sang url của dịch vụ để có thể truy cập được

    :param app_name:
    :param SSOID:
    :param request:
    :param Authorize:
    :return:
    """
    db_name = await fasty.JWT.get_db_name_async(default_db_name)
    if db_name is None:
        return Response(status_code=403)
    db_context= get_db_context(db_name)
    ret_item = await db_context.find_one_async(
        fasty.JWT_Docs.SSOs,
        fasty.JWT_Docs.SSOs.SSOID==SSOID
    )
    ret_url=ret_item.get(fasty.JWT_Docs.SSOs.ReturnUrlAfterSignIn.__name__,fasty.config.app.root_url)
    Authorize.set_access_cookies(ret_item[fasty.JWT_Docs.SSOs.Token.__name__])
    ret_url = request.query_params.get('ret',ret_url)


    res = RedirectResponse(url=ret_url, status_code=status.HTTP_303_SEE_OTHER)
    res.set_cookie("access_token_cookie",ret_item[fasty.JWT_Docs.SSOs.Token.__name__])
    return res
