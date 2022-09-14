from flask_restful import Resource
import flask_restful
import api_models.Model_Files
import fwebapi.database
import api_models.ModelApps
import db_connection

cnn = db_connection.connection


class Apps(Resource):
    """
    Lấy danh sách các apps
    """

    def post(self, app_name):
        """
        Chỉ xử lý với trường hợp app_name là admin
        :param app_name:
        :return:
        """
        if app_name != "admin":
            return []
        apps = api_models.ModelApps.sys_applications(cnn, fwebapi.database.db_config["authSource"])
        apps.sort(
            apps.RegisteredOn.desc(), # sắp xếp mới nhất lên trước
            apps.Name.asc() # tên tăng dần
        )
        return list(apps)
