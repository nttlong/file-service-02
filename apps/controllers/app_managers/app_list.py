import cy_kit
import cy_web
import fastapi
import apps.services.apps
import apps.containers
@cy_web.post("{app_name}/apps")
async def get_list(app_name, token: str = fastapi.Depends(cy_web.auth())):
    app_services = cy_kit.single(apps.services.apps.AppServices)
    ret=app_services.get_list(app_name)
    return ret