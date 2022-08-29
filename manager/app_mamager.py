import pymongo.database
import api_models.ModelApps
from api_models.ModelApps import sys_applications
from db_connection import default_db_name
def create_app(db:pymongo.database.Database, app: dict):
    if app["Name"]=="admin":
        app["Name"]=default_db_name
    apps =sys_applications(db)
    # try:
    app=apps.insert_one(app)
    return app
    # except Exception as e:
    #     raise e
def get_app_by_name(db:pymongo.database.Database,app_name:str)->api_models.ModelApps.sys_applications:
    apps= sys_applications(db)
    if app_name=="admin":
        return apps.find_one(apps.Name == default_db_name)
    return apps.find_one(apps.Name==app_name.lower())

