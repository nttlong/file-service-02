


def get_dir(directory: str):
    return directory


from fastapi import Depends, Response
import cy_web
import os
@cy_web.get("/{directory:path}")
async def page_single(directory: str = Depends(get_dir)):
    import apps.server
    directory = directory.split('?')[0]
    check_dir_path = os.path.join(apps.server.web_app.static_dir, "views", directory.replace('/', os.sep))

    if not os.path.exists(check_dir_path):
        return Response(status_code=401)

    # host_services = enig.create_instance(enig_frames.services.hosts.Hosts)
    data = dict(
        host_url=apps.server.web_app.host_url,
        full_app_url=apps.server.web_app.host_url + "/",
        host_dir=apps.server.web_app.host_dir,
        host_api_url=apps.server.web_app.host_api_url
    )

    return apps.server.web_app.templates.TemplateResponse("index.html", {"request": data})
