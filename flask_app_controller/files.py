
from flask_restful import Resource

import api_models.Model_Files
import api_models.ModelApps
import re

import db_connection
cnn = db_connection.connection

from flask import request
import flask_ext_app


class Files(Resource):
    def post(self, app_name):
        app_config = flask_ext_app.get_config()
        json_data = request.get_json(force=True)
        page_index = json_data.get("PageIndex", 0)
        page_size = json_data.get("PageSize", 20)
        field_search = json_data.get("FieldSearch", None)
        value_search = json_data.get("ValueSearch", None)
        files = api_models.Model_Files.DocUploadRegister(cnn, app_name)
        if field_search is not None and value_search is not None:
            files.filter(
                getattr(files, field_search) == re.compile(value_search)
            )
        files.skip(page_index * page_size)
        files.limit(page_size)
        ret = list(files)
        for x in ret:
            x["UrlOfServerPath"] = f"{app_config.full_url_app}/{self.endpoint}/{app_name}/directory/{x['FullFileName']}"

        return ret



