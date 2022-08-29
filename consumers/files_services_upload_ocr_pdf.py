"""
Lưu ý:
 Với các file đã đươc OCR có thể bị lỗi

"""
import json
import threading

import config
import bson
import logging
import subprocess
from concurrent.futures import ThreadPoolExecutor
import mongo_db
import ReCompact_Kafka.consumer

import api_models.Model_Files
import ReCompact.dbm.DbObjects
import ReCompact.db_context
import datetime
from multiprocessing import Process, Queue
import pdfplumber

topic = "files.services.upload.ocr.pdf"

import ocrmypdf


def runner(file_path, out_put_file_path):
    fx = ocrmypdf.ocr(
        input_file=file_path,
        output_file=out_put_file_path,
        progress_bar=False,
        language="vie+eng",
        use_threads=False,
        skip_text=True,
        jobs=100,
        keep_temporary_files=True
    )
    return fx


def handler_theading(
        consumer: ReCompact_Kafka.consumer.Consumer_obj,
        msg,
        logger: logging.Logger
):
    data = consumer.get_json(msg)
    file_path = data["FilePath"]
    upload_info = data["UploadInfo"]
    app_name = data["AppName"]
    upload_id = upload_info["_id"]

    logger.info("----------------------------------------")
    logger.info(f"Process topic {topic}")
    logger.info(json.dumps(data))
    logger.info("----------------------------------------")
    import logging
    import os
    import subprocess
    import sys
    out_put_dir = os.path.join(config.tmp_dir_ocr, app_name)
    if not os.path.isdir(out_put_dir):
        os.makedirs(out_put_dir)
    out_put_file_path = os.path.join(out_put_dir, f"{upload_id}.pdf")
    """
    Kiểm tra nôi dung file đã được ORC chưa?
    """
    doc_path =os.path.join(config.fs_crawler_path,app_name);
    if not os.path.isdir(doc_path):
        os.makedirs(doc_path)
    fs_craller_path = os.path.join(config.fs_crawler_path,app_name, f"{upload_id}.pdf").replace('/',os.sep)
    # import shutil
    # if os.path.isfile(file_path):
    #     shutil.copy(file_path, fs_craller_path)
    # if not re_process.config.is_debug:

    # file_path = input = r"\\192.168.18.36\Share\00002.pdf"

    try:
        if os.path.isfile(file_path):
            file_path = file_path.replace('/', os.sep)
            with pdfplumber.open(file_path) as pdf:
                page = pdf.pages[0]
                text = page.extract_text()
                if text.__len__()==0:
                    out_put_file_path = out_put_file_path.replace('/', os.sep)
                    runner(file_path, out_put_file_path)
                    # import concurrent.futures
                    # data = consumer.get_json(msg)
                    # with concurrent.futures.ProcessPoolExecutor() as executor:
                    #     f = executor.submit(runner, file_path, out_put_file_path)
                    #     ret = f.result()  # will rethrow any exceptions
                    #     logger.info("----------------------------------------")
                    #     logger.info(f"Threading process topic {topic} is commplate")
                    #     logger.info(json.dumps(data))
                    #     logger.info("----------------------------------------")
                    # import os

                    # exec_path=r"C:\source\lv-files-backgound-services\venv\Scripts\ocrmypdf.exe"
                    # cmd = [exec_path, "--deskew", file_path, out_put_file_path]
                    # logger.info(f"OCR file {file_path} to {out_put_file_path}")
                    # logger.info("----------------------------------------------")
                    # logging.info(cmd)
                    # logger.info("----------------------------------------------")
                    # proc = subprocess.Popen(
                    #    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    # proc.communicate() #Đợi
                    # result = proc.stdout.read()
                    # if proc.returncode == 6:
                    #    print("Skipped document because it already contained text")
                    # elif proc.returncode == 0:
                    #    logger.info(f"OCR file {file_path} to {out_put_file_path} is success")
                    # else:
                    #    logger.info(result)

    except FileNotFoundError as e:
        logger.info("-------------Errror file not found---------------")
        logger.debug(e.filename2)
        logger.info("----------------------------")
    except ValueError as e:
        logger.info("-------------ValueError---------------")
        logger.debug(e.args)
        logger.info("----------------------------")
    except Exception as e:
        logger.info("-------------Errror---------------")
        logger.debug(type(e))
        logger.debug(e)
        logger.info("----------------------------")
    finally:
        if os.path.isfile(out_put_file_path):
            import shutil
            shutil.copy(out_put_file_path, fs_craller_path)
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
                    ProcessOn=datetime.datetime.now(),
                    ProcessAction=topic,
                    UploadId=upload_id
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

                    ReCompact.dbm.FIELDS.MainFileId == fs._id,
                    ReCompact.dbm.FIELDS.OriginalFileId == upload_data_item.get("MainFileId"),
                    ReCompact.dbm.FIELDS.LastModifiedOn == datetime.datetime.now(),
                    ReCompact.dbm.FIELDS.DocUploadRegister.ProcessHistory == process_history

                )
            )
            import shutil
            if os.path.isfile(file_path):
                shutil.copy(file_path, fs_craller_path)
            # if upload_data_item is None:
            consumer.commit(msg)
            logger.info("----------------------------------------")
            logger.info(f"Process topic {topic} is ok")
            logger.info(json.dumps(data))
            logger.info("----------------------------------------")
            # return

        else:
            import shutil
            if os.path.isfile(file_path):
                shutil.copy(file_path, fs_craller_path)
            consumer.commit(msg)
            logger.info("----------------------------------------")
            logger.info(f"Process topic {topic} is ok")
            logger.info(json.dumps(data))
            logger.info("----------------------------------------")


def handler(
        consumer: ReCompact_Kafka.consumer.Consumer_obj,
        msg,
        logger: logging.Logger
):
    try:
        threading.Thread(target=handler_theading, args=(consumer, msg, logger,)).start()
        # import concurrent.futures
        # data = consumer.get_json(msg)
        # with concurrent.futures.ProcessPoolExecutor() as executor:
        #     f = executor.submit(handler_theading, consumer,msg,logger)
        #     ret = f.result()  # will rethrow any exceptions
        #     logger.info("----------------------------------------")
        #     logger.info(f"Threading process topic {topic} is commplate")
        #     logger.info(json.dumps(data))
        #     logger.info("----------------------------------------")

        # queue = Queue()
        # p = Process(target= handler_theading,args=(consumer,msg,logger,))
        # p.start()
        # p.join()  # this blocks until the process terminates
        # result = queue.get()
        # data = consumer.get_json(msg)

    except Exception as e:
        logger.debug(e)


def error(err, msg, logger):
    logger.debug(err)


import uuid

__id__ = str(uuid.uuid4())

import ReCompact_Kafka.consumer
import os
import pathlib
dir = os.path.join( str(pathlib.Path(__file__).parent),"temp")
if not os.path.isdir(dir):
    os.makedirs(dir)
os.environ['TEMP']=dir
consumer = ReCompact_Kafka.consumer.create(
    topic_id=topic,
    group_id=f"{topic}.{__id__}",
    server=config.kafka_broker,
    on_consum=handler,
    on_consum_error=error,
)

if __name__ == "__main__":
    consumer.run()
# C:\dj-apps-2022-05-25\jd-apps\venv\Scripts\python.exe C:\dj-apps-2022-05-25\jd-apps\consumers\files_services_upload_ocr_pdf.py