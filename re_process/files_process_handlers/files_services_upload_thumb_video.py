import datetime
import logging

import ReCompact_Kafka.consumer
import ReCompact.thumbnal
import api_models.Model_Files
import re_process.mongo_db
import ReCompact.db_context
import ReCompact.dbm.DbObjects
from moviepy.editor import *

def handler(
        consumer: ReCompact_Kafka.consumer.Consumer_obj,
        msg,
        logger:logging.Logger
        ):
    """
    Thủ tục xử lý ảnh thum cho file video
    :param consumer:
    :param msg:
    :param logger:
    :return:
    """
    data = consumer.get_json(msg)
    file_path = data["FilePath"]
    app_name = data["AppName"]
    upload_info = data["UploadInfo"]
    upload_id = upload_info["_id"]
    scale_width,scale_height = upload_info.get("ThumbWidth",700),upload_info.get("ThumbHeight",700)
    stream =ReCompact.thumbnal.video_create_thumb(
        in_put= file_path,
        scale_witdh=scale_width,
        scale_height =scale_height,
        second=0


    )
    db = re_process.mongo_db.get_db(app_name)
    fs = ReCompact.db_context.create_mongodb_fs_from_io_array(
        db=db,
        stm=stream

    )
    clip = VideoFileClip(
        file_path
    )
    ReCompact.dbm.DbObjects.update(
        db,
        data_item_type= api_models.Model_Files.DocUploadRegister,
        filter=ReCompact.dbm.FILTER._id==upload_id,
        updator= ReCompact.dbm.SET(
            ReCompact.dbm.FIELDS.ThumbFileId==fs._id,
            ReCompact.dbm.FIELDS.HasThumb==True,
            ReCompact.dbm.FIELDS.LastModifiedOn==datetime.datetime.now(),
            ReCompact.dbm.FIELDS.VideoDuration ==clip.duration,
            ReCompact.dbm.FIELDS.VideoFPS == clip.fps,
            ReCompact.dbm.FIELDS.VideoResolutionWidth == clip.size[0],
            ReCompact.dbm.FIELDS.VideoResolutionHeight == clip.size[1],
        )
    )
    consumer.commit(msg)
