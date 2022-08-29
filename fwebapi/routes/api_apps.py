from . import app
from . import api
from . import app_config
from flask_restful import Resource
import flask_restful
import api_models.Model_Files
import pymongo.mongo_client
import asyncio
import quicky
import datetime
import fwebapi.database
import api_models.ModelApps

cnn = fwebapi.database.connection

from flask import Flask, jsonify, request
class Apps(Resource):
    def post(self, app_name):
        if app_name != "admin":
            return []
        apps = api_models.ModelApps.sys_applications(cnn,fwebapi.database.db_config["authSource"])
        apps.sort(
            apps.RegisteredOn.desc(),
            apps.Name.asc()
        )
        return list(apps)

class App(Resource):
    def post(self, app_name):
        json_data = request.get_json(force=True)
        find_app_name = json_data.get("AppName",None)

        if app_name != "admin":
            return []
        apps = api_models.ModelApps.sys_applications(cnn,fwebapi.database.db_config["authSource"])
        ret =apps.find_one(apps.Name==find_app_name)
        return ret
api.add_resource(App, app_config.get_route_path('/apps/<app_name>/get'))

