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
from db_connection import connection, default_db_name
from . import api_files_schema
from fastapi import Body
from pydantic import BaseModel, Field
from fastapi import Depends,Response
import api_models.documents as docs
import fasty.JWT
import ReCompact.db_async
from . models import AppInfo




@fasty.api_post("/{app_name}/apps/get/{app_edit}", response_model=AppInfo)
async def application_edit(app_name: str, app_edit: str,token: str = Depends(fasty.JWT.oauth2_scheme)):
    """
    Cập nhật lại thông tin applcation

    :param app_name:
    :return:
    """
    if app_name!="admin":
        return Response(status_code=403)
    db_name = await fasty.JWT.get_db_name_async(app_name)
    dbctx = ReCompact.db_async.get_db_context(db_name)
    app = await  dbctx.find_one_async(docs.Apps,docs.Apps.Name==app_edit.lower())
    ret= AppInfo(
        Name= app[docs.Apps.Name.__name__],
        AppId =app["_id"],
        LoginUrl=app.get(docs.Apps.LoginUrl.__name__,None),
        Domain=app[docs.Apps.Domain.__name__],
        ReturnUrlAfterSignIn=app.get(docs.Apps.ReturnUrlAfterSignIn.__name__,""),
        CreatedOn =app.get(docs.Apps.RegisteredOn.__name__,""),
        Description =app.get(docs.Apps.Description.__name__,"")

    )
    return ret
