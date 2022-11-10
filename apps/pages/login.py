import cy_web
import fastapi
@cy_web.get("login")
def login(request:fastapi.Request):
    import apps.server


    # host_services = enig.create_instance(enig_frames.services.hosts.Hosts)
    if apps.server.web_app.host_dir is None:
        app_data = dict(
            version="1",
            full_url_app=apps.server.web_app.host_url,
            full_url_root=apps.server.web_app.host_url,
            api_url=apps.server.web_app.host_api_url,
            host_dir=apps.server.web_app.host_dir
        )
    return apps.server.web_app.templates.TemplateResponse("index.html", {"request": request, "app": app_data})