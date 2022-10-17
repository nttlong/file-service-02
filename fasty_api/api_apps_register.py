"""
API liệt kê danh sách các file
"""
import datetime

import ReCompact.dbm
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
    #Bat dau tao app
    db_context=db_async.get_db_context(default_db_name)
    app_item = await db_context.find_one_async(Apps,Apps.NameLower==Data.Name.lower())
    try:
        ret_app = await  db_context.insert_one_async(
            Apps,
            Apps.Name==Data.Name,
            Apps.NameLower==Data.Name.lower(),
            Apps.Domain==Data.Domain,
            Apps.LoginUrl==Data.LoginUrl,
            Apps.RegisteredOn==datetime.datetime.utcnow(),
            Apps.Email==Data.Email,
            Apps.Description==Data.Description,
            Apps.ReturnUrlAfterSignIn==Data.ReturnUrlAfterSignIn,

        )
        ret.Data = Data
        ret.Data.AppId=ret_app["_id"]
    except Db_Error as e:
        ret.Error=()
        ret.Error.Code=e.code
        ret.Error.Fields=e.fields
        ret.Error.Message=e.message
        return ret
    # Tạo user root cho app
    app_root_user =await fasty.JWT.create_user_async(
        Data.Name.lower(),
        Data.Username,
        Data.Password,
        Data.Email,
        IsSysAdmin=True
    )


    return ret
