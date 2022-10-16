# # import flask
# # import flask_bcrypt
# # from flask_restful import Resource, Api
# # from . import configuration
# # from flask_bcrypt import Bcrypt
# # from flask import Flask, session
# import db_connection
#
# __app__ = None
# __api_dir__ = '/api'
#
# class AppUser:
#     def __init__(self):
#         self.is_anonymous = True
#         """
#         Là nặc danh
#         """
#         self.Username:str= None
#         """
#         Username
#         """
#         self.Email:str =None
#         self.app_name:str= None
#         self.UserId:str= None
#         self.language:str = None
#
#
#
# class QuickyApp(flask.app.Flask):
#     def __init__(self, name, app_config: configuration.Config):
#         from flask_simple_captcha import CAPTCHA
#         super().__init__(
#             name,
#             static_folder=app_config.full_static_dir,
#             static_url_path=app_config.static_url,
#             template_folder=app_config.full_template_path
#         )
#         self.app_config = app_config
#         CAPTCHA_CONFIG = {'SECRET_CAPTCHA_KEY': app_config.captcha.secret_key}
#         CAPTCHA = CAPTCHA(configuration=CAPTCHA_CONFIG)
#         self.api = Api(self)
#         CAPTCHA.init_app(self)
#         self.bcrypt:flask_bcrypt.Bcrypt = Bcrypt(self)
#         """
#         Encrypt text
#             Example:
#                 pw_hash = bcrypt.generate_password_hash('hunter2')
#                 bcrypt.check_password_hash(pw_hash, 'hunter2') # returns True
#
#         """
#         # self.configuration["SESSION_PERMANENT"] = False
#         # self.configuration["SESSION_TYPE"] = "filesystem"
#         self.configuration["SESSION_PERMANENT"] = False
#         self.configuration["SESSION_TYPE"] = "mongodb"
#         self.configuration["SESSION_MONGODB"] = db_connection.connection
#         self.configuration["SESSION_MONGODB_DB"] = db_connection.default_db_name
#         self.configuration["SESSION_MONGODB_COLLECTION"] = 'sys_sessions'
#         self.secret_key=app_config.captcha.secret_key
#         """
#         Khóa mật ẩn
#         """
#         global __app__
#         __app__ = self
#     def get_user(self)->AppUser:
#         ret = AppUser()
#         if not session.get("IS_LOGIN",False):
#             return ret
#         else:
#             ret.is_anonymous =False
#             ret.Username= session.get("USER_NAME",None)
#             ret.Email = session.get("EMAIL",None)
#             ret.app_name= session.get("APP_NAME",None)
#             ret.app_name = session.get("LANGUAGE", None)
#             ret.UserId =session.get("USER_ID",None)
#             return ret
#
#     def set_user(self,user_id,username,email,app_name,language):
#         session["USER_NAME"]=username
#         session["EMAIL"]=email
#         session["APP_NAME"]=app_name
#         session["LANGUAGE"]=language
#         session["USER_ID"]=user_id
#         session["IS_LOGIN"] = True
#     def clear_user(self):
#         session.clear()
#
#
#
#
#
# def set_api_dir(path):
#     global __api_dir__
#     __api_dir__ = path
#
#
# def get_app() -> QuickyApp:
#     global __app__
#     return __app__
#
#
# def api_add_resource(controller_class, url_path: str):
#     """
#     Thêm Api resourece
#     :param controller_class: phải là một class thừa kế từ flask_restful.Resource
#     :param url_path:
#     :return:
#     """
#     if not url_path.startswith('/'):
#         raise Exception(f"'{url_path}' must start with '/")
#     if not isinstance(controller_class, type) and not issubclass(controller_class, Resource):
#         raise Exception(
#             f"{controller_class.__module__}.{controller_class.__name__} must inherit from {Resource.__module__}.{Resource.__name__}")
#     global __api_dir__
#     if __api_dir__ == '/':
#         get_app().api.add_resource(controller_class, get_app().app_config.get_route_path(url_path))
#     else:
#         get_app().api.add_resource(controller_class, get_app().app_config.get_route_path(__api_dir__ + url_path))
#
#
# def add_api_handler(path, handler, endpoint, methods=['GET']):
#     """
#     Thêm 1 api handler, có nghĩa là không dùng Api Objet mà dùng hàm
#     :param path:
#     :param handler:
#     :param endpoint:
#     :param methods:
#     :return:
#     """
#     if path[0] != '/':
#         raise Exception(f"'{path}' must start with /")
#     if not callable(handler):
#         raise Exception(
#             f"{handler.__module__}.{handler.__name__} must be a function")
#     global __api_dir__
#     if __api_dir__ == '/':
#         get_app().add_url_rule(get_app().app_config.get_route_path(path), endpoint, handler, methods)
#     else:
#         get_app().add_url_rule(get_app().app_config.get_route_path(__api_dir__ + path), endpoint, handler, methods)
#
#
# def add_handler(path, handler, endpoint, methods=['GET']):
#     """
#     Thêm một Api Object
#     :param path:
#     :param handler:
#     :param endpoint:
#     :param methods:
#     :return:
#     """
#     get_app().add_url_rule(get_app().app_config.get_route_path(path), endpoint, handler, methods)
#
#
# def safe_logger(*args, **kwargs):
#     return get_app().app_config.logger_wrapper(*args, **kwargs)
