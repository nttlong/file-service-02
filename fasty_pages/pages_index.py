import enigma
import fasty
from fastapi import FastAPI, Request,Response,Depends
import fasty.JWT
import os
@fasty.page_get("/login")
async def login(request: Request):
    app_data = dict(
        full_url_app=enigma.get_root_url(),
        full_url_root=enigma.get_root_url(),
        api_url=enigma.get_root_api_url()
    )
    return enigma.templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "app": app_data
        }
    )
@fasty.page_get("/")
async def page_index(request: Request):
    app_data =dict(
        full_url_app=enigma.get_root_url(),
        full_url_root=enigma.get_root_url(),
        api_url=enigma.get_root_api_url()
    )
    return enigma.templates.TemplateResponse(
        "index.html",
        {
            "request":request,
            "app": app_data
        }
    )
@fasty.page_get("/{directory:path}")
async def page_single(directory:str, request: Request):
    directory=directory.split('?')[0]
    check_dir_path = os.path.join(enigma.get_static_dir(),"views", directory.replace('/', os.sep))
    if not os.path.exists(check_dir_path):
        return Response(status_code=401)
    app_data =dict(
        full_url_app=enigma.get_root_url(),
        full_url_root=enigma.get_root_url(),
        api_url=enigma.get_root_api_url()
    )
    return enigma.templates.TemplateResponse(
        "index.html",
        {
            "request":request,
            "app": app_data
        }
    )

