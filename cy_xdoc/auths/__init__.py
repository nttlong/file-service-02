import cy_web
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request
from cy_xdoc import libs
import cy_kit
@cy_web.auth_type(OAuth2PasswordBearer)
class Authenticate:
    def validate(self, request: Request, username: str, application: str) -> bool:
        return True
    def validate_account(self,request: Request, username: str, password: str)->bool:


        app_name=username.split('/')[0]
        username=username.split('/')[1]
        if libs.Services.account.validate(app_name,username,password):
            return dict(
                application=app_name,
                username = username,
                is_ok=True
            )
        else:
            return dict(
                application=app_name,
                username=username,
                is_ok=False
            )
