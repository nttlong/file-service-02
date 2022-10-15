"""
API liệt kê danh sách các file
"""
import ReCompact.dbm
import fasty
from fastapi import FastAPI, Request, Response,Depends
import api_models.documents as docs
from ReCompact import db_async
import json

from . import api_files_schema
import fasty.JWT
from fastapi_jwt_auth import AuthJWT
@fasty.api_post("/{app_name}/apps")
async def get_list_of_apps(app_name: str,
                           filter: api_files_schema.Filter,
                           request: Request,
                           token: str = Depends(fasty.JWT.oauth2_scheme)
                           ):
    """
    Get list of application which  has completely register before
    \n
    :param app_name: \n If thy does not use 'admin', the API server will refuse \n
    :return: [\n {\n
        AppId:".." Id of Application, \n
        Name:"" Application name \n
        Decription:"..." Decription of app \n
    },..\n]
    """

    if app_name!='admin':
        return Response(status_code=403)
    db_name= await fasty.JWT.get_db_name_async(app_name)
    db = db_async.get_db_context(db_name)
    agg = db.aggregate(docs.Apps)
    agg.project(
        # docs.Files._id,

        docs.Apps.Name,
        docs.Apps.Domain,
        docs.Apps.LoginUrl,
        docs.Apps.ReturnUrlAfterSignIn,
        docs.Apps.Description,
        CreatedOn= docs.Apps.RegisteredOn,
        AppId=docs.Apps._id
    ).sort(
        ReCompact.dbm.FIELDS.CreatedOn.desc(),
        ReCompact.dbm.FIELDS.Name.desc()

    ).pager(
        filter.PageIndex, filter.PageSize
    )

    ret_list = await agg.to_list_async()
    return ret_list

