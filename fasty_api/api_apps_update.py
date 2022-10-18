import datetime

import ReCompact.db_async
import fasty
from fastapi import Depends, Body
import fasty.JWT
from .models import EditAppResutl,Error,ErrorType,AppInfo
import fasty.JWT
from fastapi import Response
import api_models.documents as docs

from ReCompact.db_async import get_db_context
@fasty.api_post("/{app_name}/apps/update/{app_edit}",response_model=EditAppResutl)
async def application_update(app_name: str, app_edit: str,Data: AppInfo = Body(embed=True) ,token: str = Depends(fasty.JWT.oauth2_scheme)):
    import enig_frames.containers
    db_name = enig_frames.containers.Container.db_context.get_db_name(app_name)
    ret=EditAppResutl()
    if app_name!="admin":
        return Response(status_code=403)
    db_context = get_db_context(db_name)
    app = await db_context.find_one_async(docs.Apps,docs.Apps.Name==app_edit.lower())
    if app is None:
        ret= EditAppResutl(
            Data=None,
            Error = Error(
                Code =ErrorType.DATA_NOT_FOUND.value,
                Message="App was not found",
                Fields=[]
            )
        )
        return ret
    try:
        app = await db_context.update_one_async(
            docs.Apps,
            docs.Apps.Name==app_edit.lower(),
            docs.Apps.Description==Data.Description,
            docs.Apps.Domain==Data.Domain,
            docs.Apps.LoginUrl==Data.LoginUrl,
            docs.Apps.ReturnUrlAfterSignIn==Data.LoginUrl,
            docs.Apps.ModifiedOn==datetime.datetime.utcnow()
        )
        ret.Data=Data
        return ret
    except ReCompact.db_async.Error as e:
        ret.Error=Error()
        ret.Error.Code=e.code
        ret.Error.Fields=e.fields
        ret.Error.Message =e.message
        return ret
