import pathlib
import os
import sys
import fastapi
import kink
import pydantic


sys.path.append(pathlib.Path(__file__).parent.parent.__str__())

import cy_kit

import jwt
import jose
from fastapi.exceptions import HTTPException


async def on_auth(self, request:fastapi.Request):

        if request.cookies.get('access_token_cookie', None) is not None:
            token = request.cookies['access_token_cookie']
            try:
                ret_data = jwt.decode(token, self.jwt_secret_key,
                              algorithms=[self.jwt_algorithm],
                              options={"verify_signature": False},
                              )

                setattr(request, "usernane", ret_data.get("sup"))
                setattr(request, "application_name", ret_data.get("application"))
                return token
            except jose.exceptions.ExpiredSignatureError as e:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            authorization: str = request.headers.get("Authorization")
            scheme, token = fastapi.utils.get_authorization_scheme_param(authorization)
            if not authorization or scheme.lower() != "bearer":
                if self.auto_error:
                    raise HTTPException(
                        status_code=401,
                        detail="Not authenticated",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                else:
                    return None
            try:
                ret_data = jwt.decode(token,
                                      self.jwt_secret_key ,
                                      algorithms=[self.jwt_algorithm],
                                      options={"verify_signature": False},
                                      )

                setattr(request, "usernane", ret_data.get("sup"))
                setattr(request, "application_name", ret_data.get("application"))
            except jose.exceptions.JWTError:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except jose.exceptions.ExpiredSignatureError as e:
                raise HTTPException(
                    status_code=401,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return token
@cy_kit.container()
class WebContaner:
    config = cy_kit.yaml_config("/home/vmadmin/python/v6/file-service-02/config.yml")

import cy_web
app = None
def get_app():
    global app
    return app
if __name__ =="__main__":
    web_app = cy_web.create_app(
        working_dir=pathlib.Path(__file__).parent.__str__(),
        host_url="http://172.16.13.72:8012",
        bind="0.0.0.0:8012",
        # dev_mode=True,
        static_dir="./../app_manager/static",
        template_dir= "./../app_manager/html",
        jwt_secret_key="d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7",
        jwt_algorithm="HS256",
        url_get_token="api/accounts/token"

    )

    app = web_app.app
    cy_web.on_auth(on_auth)
    cy_web.add_controller("api","./controllers")
    cy_web.uvicon_start()