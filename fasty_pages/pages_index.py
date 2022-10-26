import enig
import enig_frames.services.hosts
import enig_frames.services.web_apps
import enig_frames.containers
from fastapi import FastAPI, Request,Response,Depends
import fasty.JWT
import os
@fasty.page_get("/login")
async def login(request: Request):
    container=enig_frames.containers.Container
    # host_services = enig.create_instance(enig_frames.services.hosts.Hosts)
    app_data = dict(
        full_url_app=container.Services.host.base_ui_url,
        full_url_root=container.Services.host.root_url,
        api_url=container.Services.host.base_api_url,
        host_dir = container.config.config.host_dir
    )
    return container.Services.web.render(
        file="index.html",
        data={
            "request": request,
            "app": app_data
        }
    )
@fasty.page_get("/")
async def page_index(request: Request,token: str = Depends(fasty.JWT.oauth2_scheme)):
    container = enig_frames.containers.Container
    # host_services = enig.create_instance(enig_frames.services.hosts.Hosts)
    app_data = dict(
        full_url_app=container.Services.host.base_ui_url,
        full_url_root=container.Services.host.root_url,
        api_url=container.Services.host.base_api_url,
        host_dir = container.config.config.host_dir
    )
    return container.Services.web.render(
        file="index.html",
        data={
            "request": request,
            "app": app_data
        }
    )
@fasty.page_get("/{directory:path}")
async def page_single(directory:str, request: Request,token: str = Depends(fasty.JWT.oauth2_scheme)):
    container = enig_frames.containers.Container
    directory=directory.split('?')[0]
    check_dir_path = os.path.join(container.config.static_dir,"views", directory.replace('/', os.sep))
    host_services = enig.create_instance(enig_frames.services.hosts.Hosts)
    web_app = enig.create_instance(enig_frames.services.web_apps.WebApp)
    if not os.path.exists(check_dir_path):
        return Response(status_code=401)
    container = enig_frames.containers.Container
    # host_services = enig.create_instance(enig_frames.services.hosts.Hosts)
    app_data = dict(
        full_url_app=container.Services.host.base_ui_url,
        full_url_root=container.Services.host.root_url,
        api_url=container.Services.host.base_api_url,
        host_dir = container.config.config.host_dir
    )
    return container.Services.web.render(
        file="index.html",
        data={
            "request": request,
            "app": app_data
        }
    )


