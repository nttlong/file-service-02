"""
Lưu ý:
 Với các file đã đươc OCR có thể bị lỗi

"""
import config
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor

import ReCompact_Kafka.consumer
import config
import mongo_db
topic = "files.services.upload.ocr.image"
import ReCompact.dbm.DbObjects
import ReCompact.db_context
import ReCompact
import api_models.Model_Files
import datetime
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
    mime_type = upload_info["MimeType"]
    if not "image/" in mime_type:
        consumer.commit(msg)
        return
    import bson

    logger.info(data)
    import logging
    import os
    import subprocess
    import sys
    temp_dir_pdf = os.path.join(config.tmp_dir_ocr,"image_to_pfd")
    if not os.path.isdir(temp_dir_pdf):
        os.makedirs(temp_dir_pdf)
    temp_pdf_file = os.path.join(temp_dir_pdf,upload_id+".pdf")
    if not os.path.isfile(temp_pdf_file):
        """
        Chuyen file anh sang pdf
        """
        import img2pdf
        from PIL import Image
        import os
        image = Image.open(file_path)
        pdf_bytes = img2pdf.convert(image.filename)
        file = open(temp_pdf_file, "wb")
        file.write(pdf_bytes)
        image.close()
        file.close()

    out_put_dir = os.path.join(config.tmp_dir_ocr, app_name)
    if not os.path.isdir(out_put_dir):
        os.makedirs(out_put_dir)
    out_put_file_path = os.path.join(out_put_dir,f"{upload_id}.pdf")
    """
    Kiểm tra nôi dung file đã được ORC chưa?
    """
    fs_craller_path = os.path.join(config.fs_crawler_path,f"{upload_id}.pdf")

    # if not re_process.config.is_debug:
    import ocrmypdf
    # file_path = input = r"\\192.168.18.36\Share\00002.pdf"

    try:
        ret= ocrmypdf.api.ocr(
            input_file=temp_pdf_file,
            output_file= out_put_file_path,
            progress_bar=False
        )
        print(ret)
        # cmd = ["ocrmypdf", "--deskew", temp_pdf_file, out_put_file_path]
        # logger.info(f"OCR file {temp_pdf_file} to {out_put_file_path}")
        # logging.info(cmd)
        # proc = subprocess.Popen(
        #     cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # proc.communicate() #Đợi
        # logger.info(f"OCR file {file_path} to {out_put_file_path} is success")
    except Exception as e:
        logger.debug(e)
    finally:
        if os.path.isfile(out_put_file_path):
                import shutil
                shutil.copy(out_put_file_path,fs_craller_path)
                db = mongo_db.get_db(app_name)
                upload_data_item = ReCompact.dbm.DbObjects.find_one_to_dict(
                    db=db,
                    data_item_type=api_models.Model_Files.DocUploadRegister,
                    filter=ReCompact.dbm.FILTER._id == upload_id
                )
                process_history = upload_info.get("ProcessHistories", [])
                process_history += [
                    dict(
                        _id=bson.ObjectId(),
                        ProcessAction=topic,
                        UploadId=upload_id,
                        ProcessOn=datetime.datetime.now()
                    )
                ]

                fs = ReCompact.db_context.create_mongodb_fs_from_file(
                    db=db,
                    full_path_to_file=out_put_file_path

                )
                ReCompact.dbm.DbObjects.update(
                    db,
                    data_item_type=api_models.Model_Files.DocUploadRegister,
                    filter=ReCompact.dbm.FILTER._id == upload_id,
                    updator=ReCompact.dbm.SET(

                        ReCompact.dbm.FIELDS.OCRFileId == fs._id,
                        ReCompact.dbm.FIELDS.OriginalFileId == upload_data_item.get("OriginalFileId"),
                        ReCompact.dbm.FIELDS.LastModifiedOn == datetime.datetime.now(),
                        ReCompact.dbm.FIELDS.DocUploadRegister.ProcessHistory == process_history

                    )
                )
                consumer.commit(msg)
        else:
            import shutil
            shutil.copy(file_path, fs_craller_path)
            consumer.commit(msg)

def error(err,msg,logger):
    logger.debug(err)

import uuid
__id__ = str(uuid.uuid4())

import ReCompact_Kafka.consumer
consumer = ReCompact_Kafka.consumer.create(
    topic_id=topic,
    group_id=f"{topic}.{__id__}",
    server=config.kafka_broker,
    on_consum=handler,
    on_consum_error=error,
)
if __name__ == "__main__":
    consumer.run()