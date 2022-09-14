import datetime

from flask import request, Response
import quicky.object_constraints
import api_models.Model_Files
import quicky
from . base_api import BaseApi
class FileDelete(BaseApi):
    def post(self,app_name):
        data = request.get_json(force=True)
        if data.get("UploadId",None) is None:
            err= quicky.object_contraints.Error()
            err.field="UploadId"
            err.message="UploadId is require"
            err.code=quicky.object_contraints.ErrorCode.REQUIRE
            return dict(
                error=err
            )
        files = api_models.Model_Files.DocUploadRegister(self.connection,app_name)
        files.delete_one(
            files._id==data["UploadId"]
        )
        return data

quicky.api_add_resource(FileDelete, "/files/<app_name>/delete")