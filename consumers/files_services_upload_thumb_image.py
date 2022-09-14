import config
import datetime
import logging
import os.path

import bson
from PIL import Image
import ReCompact_Kafka.consumer
import ReCompact.thumbnal
import api_models.Model_Files
import mongo_db
import ReCompact.db_context
import ReCompact.dbm.DbObjects
from moviepy.editor import *
import ReCompact_Kafka.consumer
import mongo_db
import uuid
topic = "files.services.upload.thumb.image"
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
    upload_info = data["UploadInfo"]
    upload_id = upload_info["_id"]
    app_name =data ["AppName"]
    thumb_width =upload_info.get("ThumbWidth",700)
    thumb_height = upload_info.get("ThumbHeight",700)
    if not os.path.isfile(file_path):
        consumer.commit(msg)
        return
    logger.info(f"Create image Thumb file {file_path}")
    logger.info(data)
    image = Image.open(file_path)
    h,w = image.size
    thumb_dir = os.path.join(config.temp_thumbs, app_name)
    thumb_file_path = os.path.join(thumb_dir,upload_id+".png")
    if w<=thumb_width and h<=thumb_height:
        thumb_file_path = file_path
    else:
        if not os.path.isfile(thumb_file_path):
            rate = float(thumb_width/w)
            if h>w:
                rate =float(thumb_height/h)
            nh,nw = rate*h,rate*w
            if not os.path.isdir(thumb_dir):
                os.makedirs(thumb_dir)
            image.thumbnail((nh, nw))
            image.save(thumb_file_path)
            image.close()
    db = mongo_db.get_db(app_name)
    try:
        upload_data_item = ReCompact.dbm.DbObjects.find_one_to_dict(
            db =db,
            data_item_type= api_models.Model_Files.DocUploadRegister,
            filter= ReCompact.dbm.FILTER._id == upload_id

        )
        if upload_data_item is not None:
            fs = ReCompact.db_context.create_mongodb_fs_from_file(
                db,
                full_path_to_file= thumb_file_path,
                chunk_size=1024*1024
            )
            process_history = upload_info.get("ProcessHistories",[])
            process_history+=[
                dict(
                    _id=bson.ObjectId(),
                    ProcessOn = datetime.datetime.now(),
                    ProcessAction = topic,
                    UploadId = upload_id
                )
            ]

            ReCompact.dbm.DbObjects.update(
                db = db,
                data_item_type= api_models.Model_Files.DocUploadRegister,
                filter= ReCompact.dbm.FILTER._id == upload_id,
                updator= ReCompact.dbm.SET(
                    ReCompact.dbm.FIELDS.HasThumb==True,
                    ReCompact.dbm.FIELDS.ThumbFileId == fs._id,
                    ReCompact.dbm.FIELDS.ProcessHistories ==process_history,
                    ReCompact.dbm.FIELDS.LastModifiedOn == datetime.datetime.now()
                )
            )
    except Exception as e:
        logger.debug(e)
    finally:
        consumer.commit(msg)

    logger.info(f"Create image Thumb file {file_path} is finish")
    logger.info(data)



def error(err,msg,logger):
    logger.debug(err)

__id__ = str(uuid.uuid4())
consumer = ReCompact_Kafka.consumer.create(
    topic_id=topic,
    group_id=f"{topic}.{__id__}",
    server =config.kafka_broker,
    on_consum=handler,
    on_consum_error=error,
)
if __name__ == "__main__":
    consumer.run()