from fastapi import Depends, Response
import cy_web
import os


@cy_web.get("")
def home_page():
    import apps.server

    data = dict(
        host_url=apps.server.web_app.host_url,
        full_app_url=apps.server.web_app.host_url + "/",
        host_dir=apps.server.web_app.host_dir,
        host_api_url=apps.server.web_app.host_api_url
    )

    return apps.server.web_app.templates.TemplateResponse("index.html", {"request": data})

def get_dir(directory):
        return directory