import datetime
import uuid

import api_models.Model_Users
from flask import render_template,redirect, request, session
import quicky
from db_connection import connection,default_db_name
from manager import app_mamager, user_manager

app =quicky.get_app()
@app.route(app.app_config.get_route_path('/signout'))
def do_sign_out():
    url = request.url
    session.clear()
    return redirect("./")



@app.route(app.app_config.get_route_path('/login'))
def single_page_login():
    admin_db=connection.get_database(default_db_name)
    admin_app_doc = app_mamager.sys_applications(admin_db)

    admin_app = app_mamager.get_app_by_name(admin_db, default_db_name)
    if admin_app is None:
        admin_app_obj= app_mamager.sys_applications(
            admin_app_doc.Name==default_db_name,
            admin_app_doc.Domain == "localhost",
            admin_app_doc.LoginUrl == "~/login",
            admin_app_doc.ReturnUrlAfterSignIn == "~/",
            admin_app_doc.SecretKey==str(uuid.uuid4()),
            admin_app_doc.RegisteredBy=="system",
            admin_app_doc.RegisteredOn== datetime.datetime.now()
        )
        admin_app=app_mamager.create_app(db=connection.get_database(default_db_name), app= admin_app_obj.DICT)
    dict_user = user_manager.get_user_by_name(admin_db, "root")
    if dict_user is None:
        user_doc = api_models.Model_Users.User(admin_db)
        """
        Mongo document of User
        Tạo mộ Mongodb Document cho user
        """
        user_object = api_models.Model_Users.User(
            user_doc.Username=="root",
            user_doc.Email=="root@local.com",
            user_doc.UsernameLowerCase=="root",
            user_doc.Password=="root",
            user_doc.Application == admin_app
        )
        """
        Đối tượng thực user
        """
        dict_user = user_manager.create_user(admin_db, user_object.DICT)
    return render_template('login.html',app=app.app_config)
@app.route(app.app_config.get_route_path('/<path:path>'))
def single_page_app(path):
    if app.get_user().is_anonymous:
        return redirect(f"{app.app_config.full_url_root}/login", code=302)
    return render_template('index.html',app=app.app_config)

@app.route(app.app_config.get_route_path('/'))
def index():
    if app.get_user().is_anonymous:
        return redirect(f"{app.app_config.full_url_root}/login", code=302)

    return render_template('index.html',app=app.app_config)