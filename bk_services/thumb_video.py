import pathlib
import sys


sys.path.append(str(pathlib.Path(__file__).parent))
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from jarior import loggers
logger = loggers.get_logger(
        logger_name=str(pathlib.Path(__file__).stem),
        logger_dir=str(pathlib.Path(__file__).parent.parent)
    )
try:
    from bk_services import config
    from bk_services import graphic_utils
    from datetime import datetime

    import api_models.Model_Files
    import os.path

    from fasty import mime_data
    import mimetypes
    import ReCompact.thumbnal
    from moviepy.editor import *

    from jarior import loggers
    from  jarior import client
    from jarior.client import Context
    from bk_services import mongodb as mongo_db
    path = config.watch_path
    working_folder_name = pathlib.Path(__file__).stem
    working_path = os.path.join(pathlib.Path(__file__).parent,working_folder_name)
    temp_image_dir= os.path.join(working_path,"tmp-image")
    temp_thumbs_dir = os.path.join(working_path, "tmp-thumbs")
    if not os.path.isdir(temp_image_dir):
        os.makedirs(temp_image_dir)
    if not os.path.isdir(temp_thumbs_dir):
        os.makedirs(temp_thumbs_dir)
    sys.path.append(working_path)
    if not os.path.isdir(working_path):
        os.makedirs(working_path)

    def handler(context: Context):
        try:
            full_file_path = context.files[0]
            a, b = mimetypes.guess_type(full_file_path)
            if 'video/' in a:

                file_name = pathlib.Path(full_file_path).name
                app_name=context.info.get('app_name')
                file_name_only,ext = tuple(file_name.split('.'))
                upload_id= file_name_only
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

                scale_width,scale_height=350,350
                stream = ReCompact.thumbnal.video_create_thumb(
                    in_put=real_file_path,
                    scale_witdh=scale_width,
                    scale_height=scale_height,
                    second=0

                )
                tmp_image_file = os.path.join(temp_image_dir,f"{upload_id}.png")

                with open(tmp_image_file, 'wb') as out:  ## Open temporary file as bytes
                    out.write(stream.read())
                stream.close()
                del stream
                defaut_thumb_file = graphic_utils.make_thumb(
                    temp_thumbs_dir, tmp_image_file, 350,  app_name, upload_id
                )
                fs = ReCompact.db_context.create_mongodb_fs_from_file(
                    db,
                    full_path_to_file=defaut_thumb_file,
                    chunk_size=1024 * 1024
                )
                thumb_sizes = context.info.get('thumb_sizes')
                if thumb_sizes is not None:
                    graphic_utils.make_thumbs(temp_thumbs_dir, tmp_image_file, thumb_sizes, db, app_name, upload_id)
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

                logger.info(full_file_path)
        except Exception as e:
            logger.debug(e)


    from bk_services import arg_reader
    arg_config = arg_reader.get_config()
    # arg_config.msg_folder = r"/home/vmadmin/python/file-service-02/tmp/msg"
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
