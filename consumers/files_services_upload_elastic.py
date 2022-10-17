"""
Chuyển tài liệu có nôi dung văn bản cho elastic search_engine
"""
import config
import logging

import ReCompact_Kafka.consumer
import os

import shutil


def handler(
        consumer: ReCompact_Kafka.consumer.Consumer_obj,
        msg,
        logger: logging.Logger
):
    data = consumer.get_json(msg)
    app_name = data["AppName"]
    file_path = data["FilePath"]
    upload_info = data["UploadInfo"]
    file_ext = upload_info["FileExt"]
    if file_ext == "pdf":
        consumer.commit(msg)
        return
    out_put_folder = os.path.join(config.fs_crawler_path, app_name)
    if not os.path.isdir(out_put_folder):
        os.makedirs(out_put_folder)
    shutil.copy(file_path, out_put_folder)
    logger.info(f"Copy file {file_path} to {out_put_folder}")
    consumer.commit(msg)

def error(err,msg,logger):
    logger.debug(err)

import uuid
__id__ = str(uuid.uuid4())
import ReCompact_Kafka.consumer
consumer = ReCompact_Kafka.consumer.create(
    topic_id="files.services.upload.elastic",
    group_id=f"files.services.upload.elastic.{__id__}",
    server =config.kafka_broker,
    on_consum=handler,
    on_consum_error=error,
)
if __name__ == "__main__":
    consumer.run()
#C:\dj-apps-2022-05-25\jd-apps\venv\Scripts\python.exe C:\dj-apps-2022-05-25\jd-apps\consumers\files_services_upload_elastic.py