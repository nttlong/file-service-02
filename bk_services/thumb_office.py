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


    import uuid
    import shutil
    from bk_services import config
    from datetime import datetime
    from PIL import Image
    import api_models.Model_Files
    import os.path
    from fasty import mime_data
    import mimetypes
    import ReCompact.thumbnal
    from moviepy.editor import *
    import subprocess
    from bk_services.watchers import start, Info, start_thead
    from bk_services import mongodb as mongo_db

    path = config.watch_path
    working_folder_name = pathlib.Path(__file__).stem
    working_path = os.path.join(pathlib.Path(__file__).parent, working_folder_name)
    sys.path.append(working_path)
    if not os.path.isdir(working_path):
        os.makedirs(working_path)

    temp_thumb = os.path.join(working_path, 'tmp', 'thumb-images')
    user_profile_dir = os.path.join(working_path, 'tmp', 'libre_office-user-profiles')
    if not os.path.isdir(temp_thumb):
        os.makedirs(temp_thumb)
    if not os.path.isdir(user_profile_dir):
        os.makedirs(user_profile_dir)


    def create_image_from_office_file(file_path: str):
        global temp_thumb
        global user_profile_dir
        uno = f"Negotiate=0,ForceSynchronous=1;"
        out_put_dir = temp_thumb
        user_profile_id = str(uuid.uuid4())  # Tạo user profile giả, nếu kg có điều này LibreOffice chỉ tạo 1 instance,
        # kg xử lý song song được
        full_user_profile_path = os.path.join(user_profile_dir, user_profile_id)
        pid = subprocess.Popen(
            [
                config.libre_office_path,
                '--headless',
                '--convert-to', 'png',
                f"--accept={uno}",
                f"-env:UserInstallation=file://{full_user_profile_path.replace(os.sep, '/')}",
                '--outdir',
                out_put_dir, file_path
            ],
            shell=False
        )
        ret = pid.communicate()  # Đợi
        filename_only = pathlib.Path(file_path).stem
        shutil.rmtree(full_user_profile_path)
        return os.path.join(out_put_dir, f"{filename_only}.png")


    def handler(context: Context):
        try:
            global temp_thumb
            full_file_path = context.files[0]
            fx = pathlib.Path(full_file_path)
            file_name = fx.name
            app_name= context.info.get('app_name')
            file_name_only, ext = tuple(file_name.split('.'))
            if ext != 'pdf' and ext in config.office_extension:
                logger.info(full_file_path)
                real_file_path = full_file_path
                upload_id = file_name_only
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
                image_file = create_image_from_office_file(real_file_path)
                thumb_width = upload_info.get("ThumbWidth", 350)
                thumb_height = upload_info.get("ThumbHeight", 350)

                image = Image.open(image_file)
                h, w = image.size
                thumb_dir = os.path.join(temp_thumb, app_name)
                if not os.path.isdir(thumb_dir):
                    os.makedirs(thumb_dir)
                thumb_file_path = os.path.join(thumb_dir, upload_id + ".png")
                if w <= thumb_width and h <= thumb_height:
                    shutil.copy(image_file, thumb_file_path)
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
                    os.remove(image_file)
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
                print(context.full_path)
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
