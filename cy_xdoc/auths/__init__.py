import cy_web
from fastapi.security import OAuth2PasswordBearer
from fastapi import Request


@cy_web.auth_type(OAuth2PasswordBearer)
class Authenticate:
    def validate(self, request: Request, username: str, application: str) -> bool:
        return True
    def validate_account(self,request: Request, username: str, password: str)->bool:
        raise NotImplemented