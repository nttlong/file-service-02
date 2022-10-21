"""
API liệt kê danh sách các file
"""
import datetime

import ReCompact.dbm
import api_models.documents
import fasty
from fastapi import FastAPI, Request
import api_models.documents as docs
from ReCompact import db_async
import json

from . import api_files_schema
from .models import AppInfo
from fastapi import Depends
from fastapi import Body
from .models import EditAppResutl,Error,ErrorType,AppInfo
from api_models.documents import Apps
from ReCompact.db_async import get_db_context,default_db_name,Error as Db_Error
import fasty.JWT
import fasty.JWT_Docs
import enig_frames.containers
@fasty.api_post("/{app_name}/apps/register",response_model=EditAppResutl)
async def register_new_app(app_name: str, Data:AppInfo=Body(embed=True),token: str = Depends(fasty.JWT.oauth2_scheme)):
    """
    Tạo một application mới\n
    Mỗi một application là một isolate tenant bao gồm:\n
        1- Elastich search_engine engine
        2- Mongo Database
        3- Seperated file partition

    :param app_name:
    :return:
    """
    container = enig_frames.containers.Container
    ret = EditAppResutl()
    require_fields=['Name', 'LoginUrl', 'Domain', 'ReturnUrlAfterSignIn','Username','Password' ]
    for k in require_fields:
        if Data.__dict__.get(k,None) is None:
            ret.Error= Error()
            ret.Error.Code=ErrorType.DATA_REQUIRE.value
            ret.Error.Fields=[k]
            ret.Error.Message=f"'{k}' is require"
            return ret

    if Data.Name in ["admin","adminstrator","administrators",default_db_name]:
        ret.Error = Error()
        ret.Error.Code = ErrorType.DUPLICATE_DATA.value
        ret.Error.Fields = ["Name"]
        ret.Error.Message = f"Value of 'Name' is already exists"
        return ret
    if Data.Username is None or Data.Username=='':
        Data.Username='root'
        Data.Password = 'root'

    #Bat dau tao app
    app = container.Services.applications.get_app_by_name(name=Data.Name)
    if app is not None:
        container.Services.accounts.check_root_user(
            app_name=Data.Name,
            username=Data.Username,
            password=Data.Password,
            email= Data.Email
        )
        ret.Error=Error()
        ret.Error.Code=ErrorType.DUPLICATE_DATA.name
        ret.Error.Message=f"{Data.Name} is already existing"
        ret.Error.Fields=["Name"]
        return ret

    app = container.Services.applications.create(
        name=Data.Name,
        domain=Data.Domain,
        login_url=Data.LoginUrl,
        description= Data.Description

    )
    container.Services.accounts.check_root_user(
        app_name=Data.Name,
        username=Data.Username,
        password=Data.Password,
        email=Data.Email
    )
    ret.Data=AppInfo()
    ret.Data.AppId =app[api_models.documents.Apps._id]
    ret.Data.Name = app[api_models.documents.Apps.Name]
    ret.Data.Domain =app[api_models.documents.Apps.Domain]
    ret.Data.Description = app[api_models.documents.Apps.Description]
    ret.Data.LoginUrl = app[api_models.documents.Apps.LoginUrl]


    return ret
