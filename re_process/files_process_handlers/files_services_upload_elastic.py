"""
Chuyển tài liệu có nôi dung văn bản cho elastic search_engine
"""
import logging

import ReCompact_Kafka.consumer
import os
import re_process.config
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
    out_put_folder = os.path.join(re_process.config.fs_crawler_path, app_name)
    if not os.path.isdir(out_put_folder):
        os.makedirs(out_put_folder)
    shutil.copy(file_path, out_put_folder)
    logger.info(f"Copy file {file_path} to {out_put_folder}")
    consumer.commit(msg)
