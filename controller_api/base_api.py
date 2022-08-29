import pymongo.database
from flask_restful import Resource

import api_models.Model_Files
import api_models.ModelApps
import re

import db_connection

cnn = db_connection.connection

from flask import request

import quicky
import manager
__apps__ = {}

class BaseApi(Resource):
    def __init__(self):
        self.connection = db_connection.connection
        self.default_db_name = db_connection.default_db_name
        self.app_config = quicky.get_app().app_config
    def get_db(self, app_name) -> pymongo.database.Database:
        return self.connection.get_database(app_name)
