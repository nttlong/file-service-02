from flask_restful import Resource
import fwebapi.database
import db_connection

cnn = db_connection.connection

from flask import Flask, jsonify, request


class UploadServices(Resource):
    def post(self, app_name):
        data = request.get_json(True)
        if data.get("FileName", None) is None:
            return dict(
                error=dict(
                    message="FileName was not found"
                )
            )
        return dict()
