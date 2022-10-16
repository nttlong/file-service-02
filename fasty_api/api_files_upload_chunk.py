import datetime
import os.path
import pathlib
import gc
import uuid
import enigma
import ReCompact_Kafka.producer
from fastapi import  File, Form,Response,Depends
from pydantic import BaseModel, Field
from typing import Union


import fasty
from .models import Error as ret_error
from ReCompact.db_async import get_db_context, ErrorType as db_error_type,sync as run_sync
import fasty.JWT
import api_models.documents as docs
import ReCompact.db_context
import ReCompact.dbm.DbObjects
import humanize
import threading
import jarior.emitor
import jarior.loggers
__lock__= threading.Lock()
"""
Lock dành cach meta, tránh gọi về Database nhiều lần
"""
__meta_upload_cache__ = {}
"""
Cache meta upload. Trong quá trình upload hệ thống sẽ tham khảo đến database của mongodb để xác định quá trình upload
Ví dụ: Hệ thống sẽ cần phải xác định xem nội dung upload đã đạt được bao nhiêu phần trăm.
Để xác định được thông tin này hệ thống sẽ dựa vào Id upload và tìm trong Database Record ứng với Id Upload
và tham khảo đến thông tin phần trăm upload. Quá trình upload 1 file dung lượng lớn mất nhiều thời gian và việc tham khảo đến Database sẽ xảy ra rất nhiều lần.
Để tránh việc tham khảo đến Database nhiều lần cần phải có cơ chế Cache thông tin upload.
Biến này sẽ phụ trách việc cache
"""
from api_models.Models_Kafka_Tracking import Sys_Kafka_Track
Sys_Kafka_Track_Doc= Sys_Kafka_Track()
class UploadChunkResult(BaseModel):
    SizeInHumanReadable: Union[str, None] = Field(description="Dung lương format dưới dạng text")
    SizeUploadedInHumanReadable: Union[str, None] = Field(description="Dung lương đã upload format dưới dạng text")
    Percent: Union[float, None] = Field(description="Phần trăm hoàn tất")
    NumOfChunksCompleted:Union[int,None]


class UploadFilesChunkInfoResult(BaseModel):
    Data: Union[UploadChunkResult, None] = Field(description="Kết quả nếu không lỗi")
    Error: Union[ret_error, None] = Field(description="Lỗi")


def __kafka_producer_delivery_report__(error, msg):
        """
        Hàm này dùng để tiếp nhận lỗi từ Kafka
        :param error:
        :param msg:
        :return:
        """
        import asyncio
        import json
        data =json.loads(msg.value().decode("utf8"))
        app_name =data["AppName"]
        topic_key =msg.topic()
        db_context = get_db_context(app_name)
        ret = db_context.insert_one(
            Sys_Kafka_Track_Doc,
            Sys_Kafka_Track_Doc.Data == data,
            Sys_Kafka_Track_Doc.Error == error,
            Sys_Kafka_Track_Doc.Topic == topic_key,
            Sys_Kafka_Track_Doc.CreatedOn == datetime.datetime.now()
        )


        if error:
            enigma.app_logger.logger.debug("------------------------------------")
            enigma.app_logger.debug("Kafka server error")
            enigma.app_logger.debug(error)
            enigma.app_logger.debug(msg)
            enigma.app_logger.debug("------------------------------------")
        else:
            enigma.app_logger.info("------------------------------------")
            enigma.app_logger.info("Kafka server recive new topic")
            enigma.app_logger.debug(error)
            enigma.app_logger.debug(msg)
            enigma.app_logger.debug("------------------------------------")

@fasty.api_post("/{app_name}/files/upload", response_model=UploadFilesChunkInfoResult)
async def files_upload(app_name: str, FilePart: bytes = File(...),
                       UploadId: Union[str, None] = Form(...),
                       Index: Union[int, None] = Form(...),
                        token: str = Depends(fasty.JWT.oauth2_scheme)
                       ):
    topic_key = "files.services.upload"
    """
    topic báo hiệu 1 file đã được upload 
    """

    path_to_broker_share=None
    """
    Đường dẫn đến file share. 
    Một số xử lý thông qua Kafka đòi hỏi phải có file đính kèm
    và file này có thể có kích thước rất lớn lên đến vài chục GB.\n
    Các tiến trình trong Consumer có thể cần tham khảo đến nội dung file.
    Ví dụ một tiến trình trong Kafka Consumer xử lý 1 file Video có dung lượng 4GB
    Tiến trình sẽ đọc file này theo đường dẫn trong biến  path_to_broker_share
    path_to_broker_share: có thể là share file trong mang LAN, nếu tiến trình xử lý không cùng nằm trên 1 PC
    
    """

    ret = UploadFilesChunkInfoResult()
    db_name = await fasty.JWT.get_db_name_async(app_name)
    db_context = get_db_context(db_name)
    gfs = db_context.get_grid_fs()
    global __meta_upload_cache__
    global __lock__
    upload_item = __meta_upload_cache__.get(UploadId)
    if not upload_item:
        __lock__.acquire()
        try:
            upload_item = await db_context.find_one_async(docs.Files,docs.Files._id==UploadId)
            __meta_upload_cache__[UploadId]=upload_item
        except Exception as ex:
            fasty.logger.logger.debug(ex)
        finally:
            __lock__.release()

    if upload_item is None:
        ret.Error=ret_error()
        ret.Error.Code=db_error_type.DATA_NOT_FOUND
        ret.Error.Fields=['UploadId']
        ret.Error.Message =f"Upload with '{UploadId}' was not found"
        gc.collect()
        return ret
    # path_to_broker_share = os.path.join(path_to_broker_share,f"{UploadId}.{upload_item.get(docs.Files.FileExt.__name__)}")
    file_size=upload_item[docs.Files.SizeInBytes.__name__]
    size_uploaded=upload_item.get(docs.Files.SizeUploaded.__name__,0)
    num_of_chunks_complete = upload_item.get(docs.Files.NumOfChunksCompleted.__name__,0)
    nun_of_chunks = upload_item.get(docs.Files.NumOfChunks.__name__,0)
    main_file_id= upload_item.get(docs.Files.MainFileId.__name__,None)
    chunk_size_in_bytes = upload_item.get(docs.Files.ChunkSizeInBytes.__name__,0)
    server_file_name =upload_item.get(docs.Files.ServerFileName.__name__)
    path_to_broker_share = os.path.join(
        enigma.get_temp_upload_dir(app_name), f"{UploadId}.{upload_item.get(docs.Files.FileExt.__name__)}")

    if num_of_chunks_complete==0:
        fs =ReCompact.db_context.mongodb_file_create(
            db_context.db.delegate,
            server_file_name,
            chunk_size_in_bytes,
            file_size=file_size
        )
        ReCompact.db_context.mongodb_file_add_chunks(db_context.db.delegate,fs._id,Index,FilePart)



        if not os.path.isfile(path_to_broker_share):
            with open(path_to_broker_share, "wb") as file:
                file.write(FilePart)
        else:
            with open(path_to_broker_share, "ab") as file:
                file.write(FilePart)

        main_file_id=fs._id
    else:
        ReCompact.db_context.mongodb_file_add_chunks(db_context.db.delegate, main_file_id, Index, FilePart)
        if not os.path.isfile(path_to_broker_share):
            with open(path_to_broker_share, "wb") as file:
                file.write(FilePart)
        else:
            with open(path_to_broker_share, "ab") as file:
                file.write(FilePart)
    size_uploaded +=len(FilePart)
    ret.Data=UploadChunkResult()
    ret.Data.Percent=round((size_uploaded*100)/file_size,2)
    ret.Data.SizeUploadedInHumanReadable= humanize.filesize.naturalsize(size_uploaded)
    num_of_chunks_complete+=1
    ret.Data.NumOfChunksCompleted=num_of_chunks_complete
    ret.Data.SizeInHumanReadable= humanize.filesize.naturalsize(file_size)
    status=0
    if num_of_chunks_complete==nun_of_chunks:
        status=1
        jarior.emitor.config(
            msg_folder="./tmp/msg",
            file_folder="",
            logger=jarior.loggers.get_logger("msg", "./logs/jarior"),
            age_of_msg_in_minutes=24 * 60

        )
        jarior.emitor.commit(
            msg_id=str(uuid.uuid4()),
            msg_type="processing",
            info=dict(
                full_file_path=path_to_broker_share,
                app_name=app_name,
                upload_id=UploadId,
                thumb_sizes=upload_item.get(docs.Files.AvailableThumbSize.__name__)

            ),
            files_path=[path_to_broker_share]
        )


            # p_path=f"{db_name}.{UploadId}.{upload_item.get(docs.Files.FileExt.__name__)}"
            # p_path = os.path.join(fasty.configuration.broker.share_directory, p_path)
            # with open(p_path,"a") as f:
            #     f.write(".")
    db_context.update_one(
        docs.Files,
        docs.Files._id == UploadId,
        docs.Files.SizeUploaded == size_uploaded,
        docs.Files.NumOfChunksCompleted == num_of_chunks_complete,
        docs.Files.Status == status,
        docs.Files.MainFileId == main_file_id

    )
    upload_item[docs.Files.SizeUploaded.__name__] = size_uploaded
    upload_item[docs.Files.NumOfChunksCompleted.__name__] = num_of_chunks_complete
    upload_item[docs.Files.Status.__name__] = status
    upload_item[docs.Files.MainFileId.__name__] = main_file_id
    gc.collect()
    del FilePart
    return ret
#
#
# @app.post("/uploadfile/")
# async def create_upload_file(file: UploadFile):
#     return {"filename": file.filename}
