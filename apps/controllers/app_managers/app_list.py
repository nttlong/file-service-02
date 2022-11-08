import cy_web
import fastapi
@cy_web.post("{app_name}/apps")
async def get_list(app_name, token: str = fastapi.Depends(cy_web.auth())):
    return [app_name,token]