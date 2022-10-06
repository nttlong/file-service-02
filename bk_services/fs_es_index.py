import pathlib

import sys


sys.path.append(str(pathlib.Path(__file__).parent))
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from jarior import loggers
from jarior import client
from jarior.client import Context


logger = loggers.get_logger(
        logger_name=str(pathlib.Path(__file__).stem),
        logger_dir=str(pathlib.Path(__file__).parent)
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

    ext_searchable_content =[
        'application/javascript',
        'text/html',
        'application/javascript'
    ]
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
        global temp_thumb
        full_file_path = context.files[0]
        fx = pathlib.Path(full_file_path)

        try:
            file_name = fx.name
            app_name= context.info.get('app_name')
            file_name_only, ext = tuple(file_name.split('.'))
            real_file_path = full_file_path
            if not os.path.isfile(real_file_path):
                return
            is_searchable = ext!='pdf' and ext in config.office_extension
            a,b = mimetypes.guess_type(real_file_path)
            if a is not None:
                is_searchable =is_searchable or a.split('/')[0]=='text'
                is_searchable = is_searchable or (a in ext_searchable_content)

            if ext!='pdf' and ext in config.office_extension:
                """
                Process all office files
                """
                path_to_es_index_in_fs_crawler = os.path.join(config.fs_crawler_path,app_name)
                if not os.path.isdir(path_to_es_index_in_fs_crawler):
                    os.makedirs(path_to_es_index_in_fs_crawler)
                dest_file_path = os.path.join(path_to_es_index_in_fs_crawler,f"{file_name_only}.{ext}")
                if os.path.isfile(dest_file_path):
                    return
                shutil.copy(real_file_path,path_to_es_index_in_fs_crawler)
                logger.info(full_file_path)
        except Exception as e:
            logger.debug(e)


    client.config(
        msg_folder="./tmp/msg",
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