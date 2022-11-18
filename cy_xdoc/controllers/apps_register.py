import cy_kit
import cy_web
from cy_xdoc.auths import Authenticate
import fastapi.params
from cy_xdoc.services.apps import AppServices
from cy_xdoc.controllers.models.apps import AppInfo, AppInfoRegister, AppInfoRegisterResult
from cy_xdoc import libs


@cy_web.hanlder(method="post", path="{app_name}/apps/register")
def get_list_of_apps(app_name: str, Data: AppInfoRegister,
                     token=fastapi.Depends(Authenticate)) -> AppInfoRegisterResult:
    data = Data.dict()
    del data["AppId"]
    app = libs.Services.app.create(**data)
    ret = AppInfoRegisterResult()
    ret.Data = app.to_pydantic()
    return ret
