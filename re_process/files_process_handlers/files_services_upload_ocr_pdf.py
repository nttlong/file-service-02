"""
Lưu ý:
 Với các file đã đươc OCR có thể bị lỗi

"""

import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor

import ReCompact_Kafka.consumer
import re_process.config


def handler(
        consumer: ReCompact_Kafka.consumer.Consumer_obj,
        msg,
        logger: logging.Logger
):
    data = consumer.get_json(msg)
    file_path = data["FilePath"]
    upload_info = data["UploadInfo"]
    app_name = data["AppName"]
    upload_id =upload_info["_id"]


    import logging
    import os
    import subprocess
    import sys
    out_put_dir = os.path.join(re_process.config.tmp_dir_ocr, app_name)
    if not os.path.isdir(out_put_dir):
        os.makedirs(out_put_dir)
    out_put_file_path = os.path.join(out_put_dir,f"{upload_id}.pdf")
    """
    Kiểm tra nôi dung file đã được ORC chưa?
    """
    fs_craller_path = os.path.join(re_process.config.fs_crawler_path,f"{upload_id}.pdf")

    # if not re_process.configuration.is_debug:
    import ocrmypdf
    # file_path = input = r"\\192.168.18.36\Share\00002.pdf"

    try:
        cmd = ["ocrmypdf", "--deskew", file_path, out_put_file_path]
        logger.info(f"OCR file {file_path} to {out_put_file_path}")
        logging.info(cmd)
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        proc.communicate() #Đợi
        logger.info(f"OCR file {file_path} to {out_put_file_path} is success")
    except Exception as e:
        logger.debug(e)
    finally:
        if os.path.isfile(out_put_file_path):
                import shutil
                shutil.copy(out_put_file_path,fs_craller_path)
                consumer.commit(msg)
        else:
            import shutil
            shutil.copy(file_path, fs_craller_path)
            consumer.commit(msg)
