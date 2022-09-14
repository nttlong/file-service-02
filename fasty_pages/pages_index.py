import fasty
from fastapi import FastAPI, Request,Response,Depends
import fasty.JWT
import os
@fasty.page_get("/login")
async def login(request: Request):
    app_data = dict(
        full_url_app=fasty.config.app.root_url,
        full_url_root=fasty.config.app.root_url,
        api_url=fasty.config.app.api_url
    )
    return fasty.config.app.templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "app": app_data
        }
    )
@fasty.page_get("/")
async def page_index(request: Request,token: str = Depends(fasty.JWT.OAuth2Redirect())):
    app_data =dict(
        full_url_app=fasty.config.app.root_url,
        full_url_root=fasty.config.app.root_url,
        api_url=fasty.config.app.api_url
    )
    return fasty.config.app.templates.TemplateResponse(
        "index.html",
        {
            "request":request,
            "app": app_data
        }
    )
@fasty.page_get("/{directory:path}")
async def page_single(directory:str, request: Request,token: str = Depends(fasty.JWT.OAuth2Redirect())):
    directory=directory.split('?')[0]
    check_dir_path = os.path.join(fasty.config.app.static,"views", directory.replace('/', os.sep))
    if not os.path.exists(check_dir_path):
        return Response(status_code=401)
    app_data =dict(
        full_url_app=fasty.config.app.root_url,
        full_url_root=fasty.config.app.root_url,
        api_url=fasty.config.app.api_url
    )
    return fasty.config.app.templates.TemplateResponse(
        "index.html",
        {
            "request":request,
            "app": app_data
        }
    )

