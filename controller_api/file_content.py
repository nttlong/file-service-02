import datetime
from urllib.parse import unquote
from flask import Response, request
import db_connection
import mimetypes
import api_models.Model_Files  # model file upload
import quicky
import threading
import ReCompact.db_context
from flask_streaming import grid_fs_stream

__cache_url__={}
__lock__ = threading.Lock();
cnn = db_connection.connection
app_config = quicky.get_app().app_config
async def source(app_name, directory):
    """
    Tải nội dung xuốn trình duyệt
    :param app_name:
    :param directory:
    :return:
    """
    app_config.logger.debug("-----------------------------")
    app_config.logger.debug(request.path)
    app_config.logger.debug(request.url)
    app_config.logger.debug("-----------------------------")
    app_config.logger.debug(directory)
    directory = unquote(directory)
    app_config.logger.debug(directory)
    t1=datetime.datetime.now()
    t2=None
    global __cache_url__
    key=f"{app_name}/{directory}".lower()
    file_id = __cache_url__.get(key,None)
    if file_id:
        g_fs = ReCompact.db_context.get_mongodb_file_by_file_id(
            db=cnn.get_database(app_name),
            file_id= file_id
        )
        mime_type, _ = mimetypes.guess_type(directory)
        resp = grid_fs_stream.streaming_content(
            mime_type=mime_type,
            request=request,
            fs=g_fs,
            streaming_segment_size_in_KB=app_config.media.streaming_segment_size_in_KB,
            streaming_buffering_in_KB=app_config.media.streaming_buffering_in_KB

        )
        g_fs.close()

        t2= datetime.datetime.now()
        n=(t2-t1).total_seconds()*1000
        resp.headers.add("time",n)
        return resp



    files = api_models.Model_Files.DocUploadRegister(cnn, app_name)
    if directory.startswith("directory/"):
        directory = directory["directoty".__len__() + 1:]

    file_item = files.find_one(files.FullFileName == directory.lower())
    if file_item is None:
        return Response(status=404)
    fs = None
    if file_item.get("MainFileId", None) is not None:
        fs = ReCompact.db_context.get_mongodb_file_by_file_id(
            file_id=file_item["MainFileId"],
            db=cnn.get_database(app_name)

        )
        __cache_url__[key] = fs._id
    else:
        fs = ReCompact.db_context.get_mongodb_file_by_file_name(
            file_name=file_item["ServerFileName"],
            db=cnn.get_database(app_name)

        )
        __cache_url__[key]=fs._id
        files.update_one(
            files.ServerFileName == file_item["ServerFileName"],
            files.set(
                files.MainFileId == fs._id
            )
        )
    if fs is None:
        return Response(status=404)
    else:
        mime_type, _ = mimetypes.guess_type(directory)

        resp =grid_fs_stream.streaming_content(
            mime_type=mime_type,
            request=request,
            fs=fs,
            streaming_segment_size_in_KB=app_config.media.streaming_segment_size_in_KB,
            streaming_buffering_in_KB=app_config.media.streaming_buffering_in_KB

        )
        t2 = datetime.datetime.now()
        n = (t2 - t1).total_seconds() * 1000
        resp.headers.add("time", n)
        fs.close()
        return resp


quicky.add_api_handler('/files/<app_name>/<path:directory>', endpoint='file-content', handler=source)
