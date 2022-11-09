import fastapi
from fastapi import Depends, Response
import cy_web
import os


@cy_web.get("")
def home_page(request:fastapi.Request):
    import apps.server


    app_data = dict(
        version="1",
        full_url_app=apps.server.web_app.host_url,
        full_url_root=apps.server.web_app.host_url,
        api_url=apps.server.web_app.host_api_url,
        host_dir=apps.server.web_app.host_dir
    )
    return apps.server.web_app.templates.TemplateResponse("index.html", {"request": request,"app": app_data})

def get_dir(directory):
        return directory