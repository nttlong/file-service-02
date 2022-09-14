import quicky
from .base_api import BaseApi
from quicky import safe_logger
from flask import Response,request
from quicky.object_constraints import constraints
@constraints()
class AppRegisteApiParams:
    """
    Description: "dsa"
Domain: "dsad"
LoginUrl: "dsa"
Name: "dsa"
ReturnUrlAfterSignIn: "dsa"
Token: "Token"
    """
    Name=(str,True)
    """
    Tên của App
    """
    Domain = (str,True)
    LoginUrl =(str,True)
    ReturnUrlAfterSignIn=(str,True)
    Description = str
    Username =(str,True)
    Password=(str,True)
    Email =(str,True)


@safe_logger()
class AppRegister(BaseApi):
    def __init__(self):
        super(AppRegister, self).__init__()
    def post(self,app_name):
        if app_name !="admin":
            return Response(status=403)
        post_data= request.get_json(force=True)
        app_register = AppRegisteApiParams(post_data)
        err = app_register.get_error()
        if err:
            return dict(
                error=err.to_dict()
            )
quicky.api_add_resource(AppRegister,url_path="/apps/<app_name>/register")