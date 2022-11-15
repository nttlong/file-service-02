import cy_kit
import cy_web
from cy_xdoc.auths import Authenticate
import fastapi.params
from cy_xdoc.services.apps import AppServices
from cy_xdoc.controllers.models.apps import AppInfo,AppInfoRegister,AppInfoRegisterResult
from cy_xdoc import inject

@cy_web.hanlder(method="post", path="{app_name}/apps/register")
def get_list_of_apps(app_name: str, Data:AppInfoRegister, injector=inject(), token=fastapi.Depends(Authenticate)) -> AppInfoRegisterResult:
    data = Data.dict()
    del data["AppId"]
    app =injector.Services.app.create(**data)
    ret= AppInfoRegisterResult()
    ret.Data= app.to_pydantic()
    return ret


