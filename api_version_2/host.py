import pathlib
import os
import sys
import fastapi
import kink
import pydantic


sys.path.append(pathlib.Path(__file__).parent.parent.__str__())

import cy_kit


class Services:
    def test(self):
        print("OK")

@cy_kit.container()
class WebContaner:
    config = cy_kit.yaml_config("/home/vmadmin/python/v6/file-service-02/config.yml")
    service:cy_kit.single(Services)
WebContaner.service.test()
import cy_web
if __name__ =="__main__":
    cy_web.create_app(
        working_dir=pathlib.Path(__file__).parent.__str__(),
        host_url="http://172.16.13.72:8012/my_app",
        bind="0.0.0.0:8012",
        # dev_mode=True,
        static_dir="./../app_manager/static",
        template_dir= "./../app_manager/html",
        jwt_secret_key="d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        jwt_algorithm="HS256",
        url_get_token="api/accounts/token"

    )
    cy_web.add_controller("api","./controllers")
    cy_web.uvicon_start()