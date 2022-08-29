"""
Dịch vụ chuyển đổi file office sang pdf để hiển thị
nội dung trực tiếp trên trình duyệt
"""
topic="files.services.upload.pdf.office"
import config
import ReCompact_Kafka.consumer

import logging

def handler_use_libre_office(consumer: ReCompact_Kafka.consumer.Consumer_obj, msg, logger: logging.Logger):
    """
    Sử dụng Libre Office
    Chú ý: Không cần bắt lỗi trong trường hợp không cần thiết
           Nếu lỗi xãy ra hệ thống sẽ tự động ghi nhận
    :param consumer:
    :param msg:
    :param logger:
    :return:
    """
    import subprocess
    import uuid
    import config
    import os
    import ReCompact.dbm.DbObjects
    import api_models.Model_Files
    import bson
    import mongo_db
    import datetime

    import time

    data = consumer.get_json(msg)
    file_path = data["FilePath"]  # Đường dẫn đến file vật lý
    upload_info = data["UploadInfo"]
    file_ext = upload_info["FileExt"]
    file_name = upload_info["FileName"]
    if file_ext == "pdf":
        """
        file pdf bỏ qua
        """
        consumer.commit(msg)
        return
    logger.info(f"Convert {file_path} to pdf")
    logger.info(data)
    app_name = data["AppName"]
    db = mongo_db.get_db(app_name)
    upload_info = data["UploadInfo"]  # Thông tin lúc upload
    upload_id = upload_info["_id"]
    pdf_file_path = os.path.join(config.temp_thumbs, app_name, f"{upload_id}.pdf")
    out_put_dir = os.path.join(config.temp_thumbs, app_name)
    if not os.path.isfile(pdf_file_path):
        user_profile_id = str(uuid.uuid4())  # Tạo user profile giả, nếu kg có điều này LibreOffice chỉ tạo 1 instance,
        # kg xử lý song song được
        full_user_profile_path = os.path.join(config.temp_libre_office_user_profile_dir, user_profile_id)
        uno = f"Negotiate=0,ForceSynchronous=1;"

        if not os.path.isdir(out_put_dir):
            os.makedirs(out_put_dir)
        if not os.path.isfile(file_path):
            print(file_path)
            return
        arg = f"--outdir {out_put_dir} {file_path.replace(os.sep, '/')}"
        arg_list = [
            f'"{config.libre_office_path}"',

            "--headless",
            "--convert-to pdf",
            f"--accept={uno}",
            f"-env:UserInstallation=file:///{full_user_profile_path.replace(os.sep, '/')}",
            arg
        ]
        full_comand_line = " ".join(arg_list)
        logger.info(full_comand_line)
        # full_comand_line = f'"{config.libre_office_path}"  --convert-to png --outdir {out_put_dir} -env:UserInstallation=file:///{full_user_profile_path.replace(os.sep, "/")} '
        logger.debug(full_comand_line)
        # full_comand_line =r'"C:\Program Files\LibreOffice\program\soffice.exe"  --convert-to png --outdir C:\test C:\test\x.docx -env:UserInstallation=file:///C:/dj-apps-2022-05-25/jd-apps/consumers/LibreOfficeTempProfiles/xxx --headless --accept=Negotiate=0,ForceSynchronous=1;'
        p = subprocess.Popen(full_comand_line, shell=False)

        ret = p.communicate()  # Đợi
        import shutil
        shutil.rmtree(full_user_profile_path)
        logger.info(f"Process file {file_path} to image is finish")
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
        full_path_to_file=pdf_file_path

    )


    ReCompact.dbm.DbObjects.update(
        db,
        data_item_type=api_models.Model_Files.DocUploadRegister,
        filter=ReCompact.dbm.FILTER._id == upload_id,
        updator=ReCompact.dbm.SET(
            ReCompact.dbm.FIELDS.PdfFileId == fs._id,
            ReCompact.dbm.FIELDS.LastModifiedOn == datetime.datetime.now(),
            ReCompact.dbm.FIELDS.DocUploadRegister.ProcessHistory == process_history

        )
    )
    consumer.commit(msg)


def error(err, msg, logger):
    logger.debug(err)


def error1(err, msg, logger):
    logger.debug(err)


import uuid

__id__ = str(uuid.uuid4())

import ReCompact_Kafka.consumer

consumer = ReCompact_Kafka.consumer.create(
    topic_id=topic,
    group_id=f"files.services.upload.pdf.office.{__id__}",
    server=config.kafka_broker,
    on_consum=handler_use_libre_office,
    on_consum_error=error,
)
if __name__ == "__main__":
    consumer.run()
# C:\dj-apps-2022-05-25\jd-apps\venv\Scripts\python.exe C:\dj-apps-2022-05-25\jd-apps\consumers\files_services_upload_thumb_office.py