import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).parent))
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from bk_services.fs_logs import get_logger


logger = get_logger(str(pathlib.Path(__file__).stem))
try:
    import shutil


    from bk_services import config
    from datetime import datetime
    from PIL import Image
    import img2pdf
    import ocrmypdf

    import api_models.Model_Files
    import os.path
    from fasty import mime_data
    import mimetypes
    import ReCompact.thumbnal
    from moviepy.editor import *

    from bk_services.watchers import start, Info,start_thead
    from bk_services import mongodb as mongo_db
    path = config.watch_path
    working_folder_name = pathlib.Path(__file__).stem
    working_path = os.path.join(pathlib.Path(__file__).parent,working_folder_name)
    sys.path.append(working_path)
    if not os.path.isdir(working_path):
        os.makedirs(working_path)

    temp_pdf_dir= os.path.join(working_path,'tmp','pdf-images')
    temp_orc_dir= os.path.join(working_path,'tmp','orc')

    if not os.path.isdir(temp_pdf_dir):
        os.makedirs(temp_pdf_dir)
    if not os.path.isdir(temp_orc_dir):
        os.makedirs(temp_orc_dir)
    def convert_image_to_pdf(file_path:str,temp_pdf_file):
        """
                Chuyen file anh sang pdf
                """

        image = Image.open(file_path)
        pdf_bytes = img2pdf.convert(image.filename)
        file = open(temp_pdf_file, "wb")
        file.write(pdf_bytes)
        image.close()
        file.close()
        return temp_pdf_file


    def handler(info: Info):
        global temp_pdf_dir
        global logger
        try:

            a, b = mimetypes.guess_type(info.full_path)
            logger.info(info.full_path)
            if 'image/' in a:

                file_name = pathlib.Path(info.rel_path).name
                app_name,file_name_only,ext = tuple(file_name.split('.'))
                upload_id= file_name_only
                real_file_path = os.path.join(info.root_path,app_name,f"{file_name_only}.{ext}")
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
                temp_pdf_file = os.path.join(temp_pdf_dir,f"{file_name_only}.pdf")
                convert_image_to_pdf(real_file_path,temp_pdf_file)
                temp_orc_file = os.path.join(temp_orc_dir,f"{file_name_only}.pdf")
                ret = ocrmypdf.api.ocr(
                    input_file=temp_pdf_file,
                    output_file=temp_orc_file,
                    progress_bar=False,
                    language="vie+eng",
                )
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
                    os.remove(temp_pdf_file)
                    fs_index_dir = os.path.join(config.fs_crawler_path,app_name)
                    if not os.path.isdir(fs_index_dir):
                        os.makedirs(fs_index_dir)
                    if os.path.isfile(temp_orc_file):
                        shutil.move(temp_orc_file,fs_index_dir)
        except Exception as e:
            logger.debug(e)


    if "no-proces" not in sys.argv:
        start_thead(path, handler, logger)
        logger.info(f"{__file__} start. should start with no-process")
    else:
        start(path, handler, logger)
        logger.info(f"{__file__} start with process")
except Exception as e:
    logger.debug(e)