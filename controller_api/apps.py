from flask_restful import Resource, Api

from flask_restful import Resource
import flask_restful
import api_models.Model_Files
import pymongo.mongo_client
import asyncio
import quicky
import datetime

import api_models.ModelApps
import db_connection

from flask import Flask, jsonify, request

from . import base_api


@quicky.safe_logger()
class Apps(base_api.BaseApi):
    def post(self, app_name):
        if app_name != "admin":
            return []
        apps = api_models.ModelApps.sys_applications(self.connection, self.default_db_name)
        apps.sort(
            apps.RegisteredOn.desc(),
            apps.Name.asc()
        )
        return list(apps)


@quicky.safe_logger()
class App(base_api.BaseApi):
    def post(self, app_name):
        json_data = request.get_json(force=True)
        find_app_name = json_data.get("AppName", None)

        if app_name != "admin":
            return []
        apps = api_models.ModelApps.sys_applications(self.connection, self.default_db_name)
        ret = apps.find_one(apps.Name == find_app_name)
        return ret


quicky.api_add_resource(Apps, '/apps/<app_name>/list')
quicky.api_add_resource(App, '/apps/<app_name>/get')
