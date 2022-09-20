import pathlib
import shutil
import sys
sys.path.append(str(pathlib.Path(__file__).parent))
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from bk_services import config
from datetime import datetime
from PIL import Image
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
print(f"Watch path={path}")
temp_thumb= os.path.join(working_path,'tmp','thumb-images')
if not os.path.isdir(temp_thumb):
    os.makedirs(temp_thumb)
def handler(info: Info):
    global temp_thumb
    a, b = mimetypes.guess_type(info.full_path)
    print(info.full_path)
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
        if upload_info.get(api_models.Model_Files.DocUploadRegister.ThumbFileId.__name__) is not None:
            return
        if not os.path.isfile(real_file_path):
            return
        thumb_width = upload_info.get("ThumbWidth", 350)
        thumb_height = upload_info.get("ThumbHeight", 350)
        scale_width,scale_height=350,350
        file_path =real_file_path
        image = Image.open(file_path)
        h, w = image.size
        thumb_dir = os.path.join(temp_thumb, app_name)
        if not os.path.isdir(thumb_dir):
            os.makedirs(thumb_dir)
        thumb_file_path = os.path.join(thumb_dir, upload_id + ".png")
        if w <= thumb_width and h <= thumb_height:
            shutil.copy(file_path,thumb_file_path)
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

        #
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
        print(a)
        print(info.full_path)


start_thead(path, handler)
# start(path, handler)