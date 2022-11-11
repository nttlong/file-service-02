import cy_web
import cy_kit
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
import apps.services.accounts
@cy_web.form_post("accounts/token")
def accounts_get_token(
        username:str,
        password:str
):

    if '/' in username:
        items = username.split('/')
        app_name = items[0]
        username = username[app_name.__len__() + 1:]
    elif '@' in username:
        items = username.split('@')
        app_name = items[-1]
        username = username[0:-app_name.__len__() - 1]

    print("XXX dasdas")