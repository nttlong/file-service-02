import os

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
# # import fwebapi.database
# # import api_models.ModelApps
# # import re
# #
# # from flask import Response, stream_with_context
# # import mimetypes
# #
# # cnn = fwebapi.database.connection
# #
# # from flask import Flask, jsonify, request
# #
# #
# # class Files(Resource):
# #     def post(self, app_name):
# #         # http://192.168.18.36:5011/api/files/app-test-dev/directory/2c071ba4-eea9-499e-8481-db580882a183/one%20of%20us.mp4
# #         json_data = request.get_json(force=True)
# #         page_index = json_data.get("PageIndex", 0)
# #         page_size = json_data.get("PageSize", 20)
# #         field_search = json_data.get("FieldSearch", None)
# #         value_search = json_data.get("ValueSearch", None)
# #         files = api_models.Model_Files.DocUploadRegister(cnn, app_name)
# #         if field_search is not None and value_search is not None:
# #             files.filter(
# #                 getattr(files, field_search) == re.compile(value_search)
# #             )
# #         files.skip(page_index * page_size)
# #         files.limit(page_size)
# #         ret = list(files)
# #         for x in ret:
# #             x["UrlOfServerPath"] = f"{app_config.full_url_app}/{self.endpoint}/{app_name}/directory/{x['FullFileName']}"
# #
# #         return ret
#
#
# api.add_resource(Files, app_config.get_route_path('/files/<app_name>/list'))
"""
Lấy danh sách các file
"""


# @app.route(app_config.get_route_path('/files/<app_name>/<path:directory>'), methods=["GET"])
