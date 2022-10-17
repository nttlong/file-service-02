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
import enig_frames.containers
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
        AppId:".." Id of Applications, \n
        Name:"" Applications name \n
        Decription:"..." Decription of app \n
    },..\n]
    """
    container = enig_frames.containers.Container
    if app_name!='admin':
        return Response(status_code=403)
    ret_list = await container.Services.applications.get_list_async(
        app_name=app_name,
        page_index=filter.PageIndex,
        page_size=filter.PageSize,
        value_search=filter.ValueSearch)
    return ret_list

