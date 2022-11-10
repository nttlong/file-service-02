


def get_dir(directory: str):
    return directory


from fastapi import Depends, Response,Request
import cy_web
import os
@cy_web.get("{directory:path}")
async def page_single(directory: str ,request: Request):
    import apps.server
    directory = directory.split('?')[0]
    check_dir_path = os.path.join(apps.server.web_app.static_dir, "views", directory.replace('/', os.sep))

    if not os.path.exists(check_dir_path):
        return Response(status_code=401)

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
