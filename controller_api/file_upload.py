import datetime

from flask import request, Response
from flask_restful import Resource
import db_connection
import quicky.object_constraints
import humanize
import api_models.Model_Files
import quicky
import uuid
import mimetypes
import os
from .base_upload_progress import FileProgressInfo
api_models.Model_Files.DocUploadRegister.NumOfChunksCompleted
cnn = db_connection.connection
app_config = quicky.get_app().app_config



@quicky.object_constraints.constraints()
class FileRegisterInfo:
    """
    Dùng để nhận các params gởi từ client cho file upload
    """
    FileName = (str, True)
    """
    tên file kiểu text bắt buộc
    """
    FileSize = (int, True)
    """
    Kích thước file kiểu số bắt buộc
    """
    ChunkSizeInKB = (int, True)
    """
    Phân đoạn
    """
    IsPublic = (bool, True)
    """
    Chế độ 
    """
    Description = (str)

@quicky.safe_logger()
class FileRegister(Resource):
    """
    Upload controller
    """

    def post(self, app_name):

        """
        Lúc đăng ký upload đi về đây
        :param app_name:
        :return:
        """
        data = FileRegisterInfo(request.get_json(force=True))
        """
        Thông tin nhận được
        """
        err = data.get_error()
        """
        Lỗi lúc parse
        """
        if err:
            """
            Trả lỗi
            """
            return dict(
                error=err.to_dict()
            )
        # Bắt đầu xử lý
        chunk_size = data.ChunkSizeInKB * 1024
        """
        Độ dài của chunk tính bằng bytes
        """
        size_in_human_readalbe = humanize.filesize.naturalsize(data.FileSize)
        """
        Kích thước của file quy ra text
        """
        num_of_chunks = int(data.FileSize / chunk_size)
        mime_type,_ = mimetypes.guess_type(data.FileName)
        if mime_type is None or mime_type=="":
            err= quicky.object_constraints.Error()
            err.code= quicky.object_constraints.ErrorCode.FILE_TYPE_IS_NOT_SUPPORT
            err.message="File Type is not support"
            return dict(
                error=err.to_dict()
            )
        filename_only, file_extension = os.path.splitext(data.FileName)
        upload_id = str(uuid.uuid4())
        if data.FileSize % chunk_size > 0:
            num_of_chunks += 1
        ret_data = {
            FileProgressInfo.UploadId: upload_id,
            FileProgressInfo.FileName: data.FileName,
            FileProgressInfo.NumOfChunksCompleted: 0,
            FileProgressInfo.ChunkSizeInBytes: chunk_size,
            FileProgressInfo.NumOfChunks: num_of_chunks,
            FileProgressInfo.Percent: float(0),
            FileProgressInfo.SizeUploadedInHumanReadable: humanize.naturalsize(0),
            FileProgressInfo.SizeUploaded: float(0),
            FileProgressInfo.MimeType: mime_type,
            FileProgressInfo.FileExt: file_extension,
            FileProgressInfo.SizeInHumanReadable:size_in_human_readalbe,
            FileProgressInfo.ServerFileName : f"{upload_id}{file_extension}",
            FileProgressInfo.FullFileName : f"{upload_id}/{data.FileName.lower()}",
            FileProgressInfo.Status:0,
            FileProgressInfo.RegisterOn:datetime.datetime.now(),
            FileProgressInfo.RegisterBy:app_name,
            FileProgressInfo.FileSize: data.FileSize,
            FileProgressInfo.ChunkSizeInKB: data.ChunkSizeInKB,
            FileProgressInfo.IsPublic: data.IsPublic,
            FileProgressInfo.ChunkIndex:int(0)



            }
        ret_data={**ret_data,**{"_id":upload_id}}
        file_progress_info = FileProgressInfo(ret_data)
        err = file_progress_info.get_error()
        """
        Kiểm tra lỗi
        """
        if err:
            """
            lỗi này không thông báo cho người dùng, thuộc về lỗi logic
            """
            app_config.logger.debug(err.as_exception())
            if app_config.debug:
                """
                Nếu đang ở chế độ debug
                """
                raise err.as_exception()
            else:
                return Response(status=500)

        files = api_models.Model_Files.DocUploadRegister(cnn,app_name)
        """
        Tạo queryable file cho MongoDb
        """
        try:
            files.insert_one(file_progress_info.to_dict())
            ret_data=file_progress_info.to_dict()
            ret_data["RelUrlOfFile"] = f"files/{app_name}/diretory/{upload_id}/{data.FileName}"
            ret_data["UrlOfFile"] = f"{app_config.api_url}/{ret_data['RelUrlOfFile']}"
            ret_data["RelThumbUrl"] = f"files/{app_name}/thumb/{upload_id}.png"
            ret_data["ThumbUrl"] = f"{app_config.api_url}/{ret_data['RelThumbUrl']}"
            return dict(
                data=ret_data
            )
        except Exception as e:
            print(e)


quicky.api_add_resource(FileRegister, "/files/<app_name>/upload/register")
