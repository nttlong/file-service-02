import pathlib
import sys
sys.path.append(str(pathlib.Path(__file__).parent))
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from bk_services import config
from datetime import datetime

import api_models.Model_Files
import os.path


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

def handler(info: Info):
    a, b = mimetypes.guess_type(info.full_path)
    if 'video/' in a:

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
        if upload_info.get(api_models.Model_Files.DocUploadRegister.ThumbFileId.__name__) is not None:
            return
        if not os.path.isfile(real_file_path):
            return
        scale_width,scale_height=350,350
        stream = ReCompact.thumbnal.video_create_thumb(
            in_put=real_file_path,
            scale_witdh=scale_width,
            scale_height=scale_height,
            second=0

        )

        fs = ReCompact.db_context.create_mongodb_fs_from_io_array(
            db=db,
            stm=stream

        )
        clip = VideoFileClip(
            real_file_path
        )
        ReCompact.dbm.DbObjects.update(
            db,
            data_item_type=api_models.Model_Files.DocUploadRegister,
            filter=ReCompact.dbm.FILTER._id == upload_id,
            updator=ReCompact.dbm.SET(
                ReCompact.dbm.FIELDS.ThumbFileId == fs._id,
                ReCompact.dbm.FIELDS.HasThumb == True,
                ReCompact.dbm.FIELDS.LastModifiedOn == datetime.utcnow(),
                ReCompact.dbm.FIELDS.VideoDuration == clip.duration,
                ReCompact.dbm.FIELDS.VideoFPS == clip.fps,
                ReCompact.dbm.FIELDS.VideoResolutionWidth == clip.size[0],
                ReCompact.dbm.FIELDS.VideoResolutionHeight == clip.size[1],
            )
        )
        print(a)
        print(info.full_path)


start_thead(path, handler)