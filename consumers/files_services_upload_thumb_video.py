import config
import datetime
import logging

import ReCompact_Kafka.consumer
import ReCompact.thumbnal
import api_models.Model_Files
import mongo_db
import ReCompact.db_context
import ReCompact.dbm.DbObjects
from moviepy.editor import *
import ReCompact.thumbnal

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

    try:
        data = consumer.get_json(msg)

        file_path = data["FilePath"]
        if not os.path.isfile(file_path):
            consumer.commit(msg)
            return
        app_name = data["AppName"]
        upload_info = data["UploadInfo"]
        upload_id = upload_info["_id"]
        scale_width,scale_height = upload_info.get("ThumbWidth",350),upload_info.get("ThumbHeight",350)
        logger.info(f"Create VideoService Thumb file {file_path}")
        logger.info(data)
        stream =ReCompact.thumbnal.video_create_thumb(
            in_put= file_path,
            scale_witdh=scale_width,
            scale_height =scale_height,
            second=0


        )
        db = mongo_db.get_db(app_name)
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
        logger.info(f"Create VideoService Thumb file {file_path} is ok")
        logger.info(data)
    except Exception as e:
        logger.info(f"Create VideoService Thumb file {file_path} is fail")
        logger.info(data)
        logger.debug(e)

def error(err,msg,logger):
    logger.debug(err)
import ReCompact_Kafka.consumer
import config
import uuid
__id__ = str(uuid.uuid4())
consumer = ReCompact_Kafka.consumer.create(
    topic_id="files.services.upload.thumb.video",
    group_id=f"files.services.upload.thumb.video.{__id__}",
    server =config.kafka_broker,
    on_consum=handler,
    on_consum_error=error,
)
if __name__ == "__main__":
    consumer.run()
#C:\dj-apps-2022-05-25\jd-apps\venv\Scripts\python.exe C:\dj-apps-2022-05-25\jd-apps\consumers\files_services_upload_thumb_video.py