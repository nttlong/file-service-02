import db_connection
import quicky
from flask import Response,Request
from . import base_api
import manager
from quicky.object_constraints import constraints
from flask import Response,request,session
import manager.user_manager
@constraints()
class LoginParams:
    username=(str,True)
    password =(str,True)
    language = (str,True)
@quicky.safe_logger()
class Login(base_api.BaseApi):
    @manager.tanent_check(Response(status=403))
    def post(self, app_name):
        params= LoginParams(request.get_json(force=True))
        error = params.get_error()
        if error:
            return dict(
                error=error.to_dict()
            )
        db =db_connection.connection.get_database(app_name)
        user = manager.user_manager.check_user(db,params.username,params.password)
        if not user:
            error= quicky.object_constraints.Error()
            error.code=quicky.object_constraints.ErrorCode.LOGIN_FAIL
            error.message="Login fail"
            return dict(
                error=error.to_dict()
            )
        quicky.get_app().set_user(
            user_id=str(user["_id"]),
            app_name=app_name,
            language=params.language,
            username=user["Username"],
            email=user["Email"]
        )
        return dict(
            data=dict(
                redirect=f"{quicky.get_app().app_config.full_url_app}"
            )
        )
quicky.api_add_resource(Login,"/accounts/<app_name>/login")
