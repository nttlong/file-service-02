from flask import Response, request
import db_connection
import mimetypes
import api_models.Model_Files  # model file upload
import quicky
import api_models.Model_Files
import ReCompact.db_context
import mimetypes
import flask_streaming.grid_fs_stream
from flask import request,Response
cnn = db_connection.connection


def thumb(app_name, file_id):
    """
    Tải nội dung xuốn trình duyệt
    :param app_name:
    :param directory:
    :return:
    """
    import os
    id,ext = file_id.split('.')
    mime_type,_ = mimetypes.guess_type(file_id)

    files = api_models.Model_Files.DocUploadRegister(cnn,app_name)
    file_object = files.find_one(files._id == id)
    fs = ReCompact.db_context.get_mongodb_file_by_file_id(cnn.get_database(app_name),
                                                          file_object[files.ThumbFileId.__name__])
    if not fs:
        return Response(status=404)
    return  flask_streaming.grid_fs_stream.streaming_content(fs,mime_type,request,fs.length,0)




quicky.add_api_handler('/files/<app_name>/thumb/<file_id>', endpoint=__name__, handler=thumb)
