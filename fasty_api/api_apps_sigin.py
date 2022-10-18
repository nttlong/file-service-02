import motor

import ReCompact.dbm
import enig_frames.services.accounts
import enig_frames.config
import fasty
from fastapi import FastAPI, Request, Header, Response
import api_models.documents as docs
from ReCompact import db_async
import json

from . import api_files_schema
from api_models.documents import Files
from ReCompact import db_async
from fastapi.responses import StreamingResponse
import os
import mimetypes
import api_models.documents
import fasty.mongo_fs_http_streaming
from  fastapi import Depends,status,Request,Response
from fastapi.responses import RedirectResponse, HTMLResponse
import urllib
import fasty.JWT
import fasty.JWT_Docs
from ReCompact.db_async import get_db_context,default_db_name
from fastapi_jwt_auth import AuthJWT
import enig
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
    accounts_services= enig.depen(enig_frames.services.accounts.Accounts)
    config =enig.depen(enig_frames.config.Configuration)
    sso_info=  await accounts_services.get_sso_login_asycn(SSOID)


    ret_url=sso_info.get(api_models.documents.SSOs.ReturnUrlAfterSignIn.__name__,config.get_root_url())
    Authorize.set_access_cookies(sso_info[api_models.documents.SSOs.Token.__name__])
    ret_url = request.query_params.get('ret',ret_url)


    res = RedirectResponse(url=ret_url, status_code=status.HTTP_303_SEE_OTHER)
    res.set_cookie("access_token_cookie",sso_info[api_models.documents.SSOs.Token.__name__])
    return res
