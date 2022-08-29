import mimetypes
import os.path

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
import ReCompact.api_input
import ReCompact.dbm
import ReCompact.db_context
import ReCompact_Kafka.producer
import api_models.Model_Files
import uuid
import datetime
import pathlib
import humanize
import openxmllib
import mimetypes
from django.core.files.uploadedfile import UploadedFile


class UploadInfo:
    """
    Map các thông lúc tạo một upload
    """
    FileName = (str, True)  # Tên file, bắt buộc
    FileSize = (int, True)  # Kích thước file, bắt buộc
    ChunkSizeInKB = (int, True)  # Kích thước chunk tính bằn KB, bắt buộc
    IsPublic = (bool, True)  # Công khai hay phải login
    ThumbWidth = int  # Độ rộng ảnh Thumb, có cũng được không có cũng chả sao, vì một số tệp làm gì có ảnh Thumb
    ThumbHeight = int  # Độ cao ảnh Thumb, có cũng được không có cũng chả sao
    ThumbFile = UploadedFile  # Nếu thích thì đính kèm ảnh thumb lúc upload


class UploadChunk:
    """
    Thông tin để upload
    """
    UploadId = (str, True)
    Index = (int, True)
    FilePart = (UploadedFile, True)


def __kafka_producer_delivery_report__(error,msg):
    fx = msg
    print(msg)


@require_http_methods(["POST"])
@ReCompact.api_input.map_param(UploadInfo)
def register(request, app_name, upload_info: UploadInfo, error: ReCompact.api_input.Error):
    if error:
        return error.to_error_500()
    db = ReCompact.db_context.get_db(app_name)
    num_of_chunk, tail = divmod(upload_info.FileSize, upload_info.ChunkSizeInKB * 1024)
    ext = pathlib.Path(upload_info.FileName).suffix
    id = str(uuid.uuid4())
    if ext.__len__() > 0:
        ext = ext[1:]
    if tail > 0:
        num_of_chunk = num_of_chunk + 1
    if not upload_info.ThumbHeight:
        upload_info.ThumbHeight = 700
    if not upload_info.ThumbWidth:
        upload_info.ThumbWidth = 700

    mime_type, err = mimetypes.guess_type(upload_info.FileName)

    try:
        upload_info.FileName = upload_info.FileName.replace('#', '-').replace('?', '-')
        upload_item = api_models.Model_Files.DocUploadRegister(
            _id=id,
            FileName=upload_info.FileName.replace('#', '-').replace('?', '-'),
            RegisterOn=datetime.datetime.now(),
            Status=0,
            SizeInBytes=upload_info.FileSize,
            ChunkSizeInKB=upload_info.ChunkSizeInKB,
            ChunkSizeInBytes=upload_info.ChunkSizeInKB * 1024,
            NumOfChunks=num_of_chunk,
            FileExt=ext,
            SizeInHumanReadable=humanize.filesize.naturalsize(upload_info.FileSize),
            PercentageOfUploaded=float(0),
            ServerFileName=f"{id}.{ext}",
            RegisteredBy=app_name,
            IsPublic=upload_info.IsPublic,
            FullFileName=f"{id}/{upload_info.FileName}".lower(),
            ThumbWidth=upload_info.ThumbWidth,
            ThumbHeight=upload_info.ThumbHeight,
            MimeType=mime_type,
            SizeUploaded=0,
            NumOfChunksCompleted=0

        )
        ret = ReCompact.dbm.DbObjects.insert(db, upload_item)
        return JsonResponse(upload_item.DICT, safe=True)
    except Exception as e:
        print(e)
        raise e


@require_http_methods(["POST"])
@ReCompact.api_input.map_param(UploadChunk)
def chunk(request, app_name, chunk_info: UploadChunk, error: ReCompact.api_input.Error):
    import ReCompact.file_object
    import web.settings
    if error:
        return error.to_error_500()
    Status = 0
    db = ReCompact.db_context.get_db(app_name)
    upload_item = ReCompact.dbm.DbObjects.find_to_object(
        db,
        api_models.Model_Files.DocUploadRegister,
        ReCompact.dbm.FILTER._id == chunk_info.UploadId
    )
    if upload_item is None:
        error = ReCompact.api_input.Error()
        error.raise_item_was_not_found()
        error.message = f"Upload with id={chunk_info.UploadId} was not found"
        return error.to_error_500()
    SizeUploaded = upload_item.SizeUploaded
    NumOfChunksCompleted = upload_item.NumOfChunksCompleted
    fs_id = None
    temp_upload_file = os.path.join(web.settings.TEMP_UPLOAD_DIR, app_name, upload_item.ServerFileName)
    if chunk_info.Index == 0:
        ReCompact.file_object.create_empty_file(temp_upload_file)
        fs = ReCompact.db_context.mongodb_file_create(
            db,
            file_name=upload_item.ServerFileName,
            chunk_size=upload_item.ChunkSizeInBytes,
            file_size=upload_item.SizeInBytes
        )
        ReCompact.dbm.DbObjects.update(
            db,
            api_models.Model_Files.DocUploadRegister,
            ReCompact.dbm.FILTER._id == upload_item._id,
            ReCompact.dbm.SET(
                ReCompact.dbm.FIELDS.MainFileId == fs._id
            )
        )
        fs_id = fs._id
    else:
        fs_id = upload_item.MainFileId
    assert isinstance(chunk_info.FilePart, UploadedFile)
    with chunk_info.FilePart.open("rb") as f:
        data = f.read()
        ReCompact.file_object.append_file(temp_upload_file, data)
        assert isinstance(data, bytes)
        SizeUploaded += data.__len__()
        ReCompact.db_context.mongodb_file_add_chunks(
            db,
            fs_id,
            chunk_info.Index,
            data
        )
    PercentageOfUploaded = round(SizeUploaded / upload_item.SizeInBytes, 2) * 100
    NumOfChunksCompleted += 1
    if NumOfChunksCompleted == upload_item.NumOfChunks:
        Status = 1
        try:
            import ReCompact.kafka_producer
            ReCompact_Kafka.producer.Bootstrap(
                web.settings.KAFKA["BROKERS"],
                delivery_report=__kafka_producer_delivery_report__
            ).send_msg_sync("files.services.upload", dict(
                AppName=app_name,
                FilePath=temp_upload_file,
                UploadInfo=upload_item.DICT

            ))
        except Exception as e:
            print(e)
    ReCompact.dbm.DbObjects.update(
        db,
        api_models.Model_Files.DocUploadRegister,
        ReCompact.dbm.FILTER._id == upload_item._id,
        ReCompact.dbm.SET(
            ReCompact.dbm.FIELDS.PercentageOfUploaded == PercentageOfUploaded,
            ReCompact.dbm.FIELDS.NumOfChunksCompleted == NumOfChunksCompleted,
            ReCompact.dbm.FIELDS.SizeUploaded == SizeUploaded,
            ReCompact.dbm.FIELDS.Status == Status,
        )
    )
    upload_item.Status = Status
    upload_item.PercentageOfUploaded = PercentageOfUploaded
    upload_item.NumOfChunksCompleted = NumOfChunksCompleted

    ret_dict = dict(
        Percent=PercentageOfUploaded,
        SizeUploadedInHumanReadable=humanize.filesize.naturalsize(SizeUploaded),
        Status=Status
    )
    # produce a new topc name file_upload

    ret_h = JsonResponse(ret_dict, safe=True)
    return ret_h
