import pathlib

import sys

sys.path.append(str(pathlib.Path(__file__).parent))
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from jarior import loggers
from jarior import client
from jarior.client import Context


logger = loggers.get_logger(
        logger_name=str(pathlib.Path(__file__).stem),
        logger_dir=str(pathlib.Path(__file__).parent.parent)
    )
try:
    import shutil
    from bk_services import config
    from datetime import datetime
    from PIL import Image
    import img2pdf
    import ocrmypdf
    import pdfplumber
    import api_models.Model_Files
    import os.path
    from fasty import mime_data
    import mimetypes
    import ReCompact.thumbnal
    from moviepy.editor import *


    from bk_services import mongodb as mongo_db

    path = config.watch_path
    working_folder_name = pathlib.Path(__file__).stem
    working_path = os.path.join(pathlib.Path(__file__).parent, working_folder_name)
    sys.path.append(working_path)
    if not os.path.isdir(working_path):
        os.makedirs(working_path)

    temp_pdf_dir = os.path.join(working_path, 'tmp', 'pdf-images')
    temp_orc_dir = os.path.join(working_path, 'tmp', 'orc')

    if not os.path.isdir(temp_pdf_dir):
        os.makedirs(temp_pdf_dir)
    if not os.path.isdir(temp_orc_dir):
        os.makedirs(temp_orc_dir)


    def detect_is_ocr(file_path: str):
        """
        Check is pdf file ready ORC?
        :param file_path:
        :return:
        """
        if not os.path.isfile(file_path):
            return True

        with pdfplumber.open(file_path) as pdf:
            """
            Check have pdf file been ORC?
            """
            if pdf.pages.__len__() == 0:
                """
                Nothing to do
                """
                return True
            for page in pdf.pages:
                text = page.extract_text()
                if text.__len__() > 0:
                    return True
            return False


    def runner(file_path, out_put_file_path):
        """
        Thuc hien ocr pdf file trong tien tring rieng biet
        :param file_path:
        :param out_put_file_path:
        :return:
        """
        try:
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
        except Exception as e:
            print(e)


    def handler(context: Context):
        try:
            global temp_pdf_dir
            full_file_path=context.files[0]
            file_name = pathlib.Path(full_file_path).name
            app_name =context.info.get('app_name')
            file_name_only, ext = tuple(file_name.split('.'))

            if ext.lower() == 'pdf':
                try:
                    logger.info(full_file_path)
                    upload_id = file_name_only
                    real_file_path = full_file_path

                    db = mongo_db.get_db(app_name)
                    upload_info = ReCompact.dbm.DbObjects.find_one_to_dict(
                        db,
                        data_item_type=api_models.Model_Files.DocUploadRegister,
                        filter=ReCompact.dbm.FILTER._id == upload_id

                    )
                    if upload_info is None:
                        return
                    if upload_info.get(api_models.Model_Files.DocUploadRegister.OCRFileId.__name__) is not None:
                        return
                    if not os.path.isfile(real_file_path):
                        return
                    is_ocr = detect_is_ocr(real_file_path)
                    fs_index_dir = os.path.join(config.fs_crawler_path, app_name)
                    if not os.path.isdir(fs_index_dir):
                        os.makedirs(fs_index_dir)
                    if is_ocr:
                        """
                        Transfer to elastic search
                        """
                        if not os.path.isfile(real_file_path):
                            return

                        shutil.copy(real_file_path,os.path.join(fs_index_dir,f"{file_name_only}.pdf"))
                        return
                    temp_orc_file = os.path.join(temp_orc_dir,f"{file_name_only}.pdf")
                    runner(real_file_path,temp_orc_file)

                    if os.path.isfile(temp_orc_file):
                        fs = ReCompact.db_context.create_mongodb_fs_from_file(
                            db=db,
                            full_path_to_file=temp_orc_file

                        )
                        ReCompact.dbm.DbObjects.update(
                            db,
                            data_item_type=api_models.Model_Files.DocUploadRegister,
                            filter=ReCompact.dbm.FILTER._id == upload_id,
                            updator=ReCompact.dbm.SET(

                                ReCompact.dbm.FIELDS.OCRFileId == fs._id,
                                ReCompact.dbm.FIELDS.LastModifiedOn == datetime.utcnow(),

                            )
                        )

                        fs_index_dir = os.path.join(config.fs_crawler_path,app_name)
                        if not os.path.isdir(fs_index_dir):
                            os.makedirs(fs_index_dir)
                        if os.path.isfile(temp_orc_file):
                            shutil.move(temp_orc_file,fs_index_dir)
                except Exception as e:
                    logger.debug(e)
        except Exception as e:
            logger.debug(e)


    client.config(
        msg_folder="./tmp/msg",
        logger=logger
    )
    th = client.watch(
        msg_type="processing",
        handler=handler,
        delay_in_second = 0.1,
        max_age_of_msg_in_minutes=10
    )
    th.join()

except Exception as e:
    logger.debug(e)
# start(path, handler)
