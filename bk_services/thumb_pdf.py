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
    import api_models.Model_Files
    import os.path

    import glob, sys, fitz
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

    temp_thumb= os.path.join(working_path,'tmp','thumb-images')
    if not os.path.isdir(temp_thumb):
        os.makedirs(temp_thumb)
    def handler(context: Context):
        try:
            global temp_thumb
            global working_path
            full_file_path = context.files[0]
            a, b = mimetypes.guess_type(full_file_path)
            if a=='application/pdf':
                logger.info(full_file_path)
                file_name = pathlib.Path(full_file_path).name
                app_name = context.info.get('app_name')
                file_name_only, ext = tuple(file_name.split('.'))
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
                if upload_info.get(api_models.Model_Files.DocUploadRegister.ThumbFileId.__name__) is not None:
                    return
                if not os.path.isfile(real_file_path):
                    return

                image_file_dir= os.path.join(working_path,"pdf-image-files")
                if not os.path.isdir(image_file_dir):
                    os.makedirs(image_file_dir)
                image_file_path=os.path.join(image_file_dir, f"{upload_id}.png")
                # To get better resolution
                zoom_x = 2.0  # horizontal zoom
                zoom_y = 2.0  # vertical zoom
                mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

                all_files = glob.glob(real_file_path)
                thumb_dir = os.path.join(temp_thumb, app_name)
                thumb_file_path = os.path.join(thumb_dir, upload_id + ".png")

                for filename in all_files:
                    doc = fitz.open(filename)  # open document
                    for page in doc:  # iterate through the pages
                        pix = page.get_pixmap()  # render page to an image
                        pix.save(image_file_path)  # store image as a PNG
                        break  # Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
                    break  # Hết vòng lặp luôn Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
                thumb_width = upload_info.get("ThumbWidth", 350)
                thumb_height = upload_info.get("ThumbHeight", 350)
                scale_width, scale_height = 350, 350
                file_path = image_file_path
                image = Image.open(file_path)
                h, w = image.size
                thumb_dir = temp_thumb

                thumb_file_path = os.path.join(thumb_dir, upload_id + ".png")
                if w <= thumb_width and h <= thumb_height:
                    shutil.copy(file_path, thumb_file_path)
                else:
                    rate = float(thumb_width / w)
                    if h > w:
                        rate = float(thumb_height / h)
                    nh, nw = rate * h, rate * w
                    if not os.path.isdir(thumb_dir):
                        os.makedirs(thumb_dir)
                    image.thumbnail((nh, nw))
                    image.save(thumb_file_path)
                    image.close()
                os.remove(image_file_path)
                fs = ReCompact.db_context.create_mongodb_fs_from_file(
                    db,
                    full_path_to_file=thumb_file_path,
                    chunk_size=1024 * 1024
                )
                ReCompact.dbm.DbObjects.update(
                    db,
                    data_item_type=api_models.Model_Files.DocUploadRegister,
                    filter=ReCompact.dbm.FILTER._id == upload_id,
                    updator=ReCompact.dbm.SET(
                        ReCompact.dbm.FIELDS.ThumbFileId == fs._id,
                        ReCompact.dbm.FIELDS.HasThumb == True,
                        ReCompact.dbm.FIELDS.LastModifiedOn == datetime.utcnow(),

                    )
                )
                os.remove(thumb_file_path)
                logger.info(full_file_path)
        except Exception as e:
            logger.debug(e)


    from bk_services import arg_reader

    arg_config = arg_reader.get_config()
    config.fs_crawler_path = arg_config.fs_crawler_path
    config.config['db'] = arg_config.db_config
    client.config(
        msg_folder=arg_config.msg_folder,
        logger=logger
    )
    th = client.watch(
        msg_type="processing",
        handler=handler,
        delay_in_second=0.1,
        max_age_of_msg_in_minutes=10
    )
    th.join()
except Exception as e:
    logger.debug(e)