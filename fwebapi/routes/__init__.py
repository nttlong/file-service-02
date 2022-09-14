import datetime

from flask import Flask  # importing flask elements to make everything work
from flask import render_template
from flask import send_from_directory
import quicky.config
import quicky.logs
import pathlib
from flask_restful import Resource, Api
from flask_cors import CORS
import pathlib
import flask_ext_app

app_config = quicky.config.Config(str(pathlib.Path(__file__).parent.parent))
from flask import json


class ModelEncoder(json.JSONEncoder):
    def default(self, o):
        if hasattr(o, 'to_json'):
            return o.to_json()
        else:
            return super(ModelEncoder, self).default(o)


app = Flask(
    __name__,
    static_folder=app_config.full_static_dir,
    static_url_path=app_config.static_url,
    template_folder=app_config.full_template_path
)
flask_ext_app.save_config(app, app_config)
app.json_encoder = ModelEncoder
CORS(app)


@app.after_request
def add_header(response):
    response.cache_control.max_age = 300
    return response


api = Api(app)
import flask_app_controller.content

app.add_url_rule(app_config.get_route_path('/files/<app_name>/<path:directory>'), "source",
                 flask_app_controller.content.source, methods=["GET"])

import flask_app_controller.apps

api.add_resource(flask_app_controller.apps.Apps, app_config.get_route_path('/apps/<app_name>/list'))
import flask_app_controller.files

api.add_resource(flask_app_controller.files.Files, app_config.get_route_path('/files/<app_name>/list'))

import  flask_app_controller.file_upload

api.add_resource(flask_app_controller.file_upload.UploadServices, app_config.get_route_path("/files/<app_name>/upload/register"))