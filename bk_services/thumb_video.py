import pathlib
import sys
sys.path.append(str(pathlib.Path(__file__).parent))
sys.path.append(str(pathlib.Path(__file__).parent.parent))
from bk_services.fs_logs import get_logger
logger = get_logger(str(pathlib.Path(__file__).stem))
try:
    from bk_services import config
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
    sys.path.append(working_path)
    if not os.path.isdir(working_path):
        os.makedirs(working_path)
    logger = loggers.get_logger(
        logger_name=str(pathlib.Path(__file__).stem),
        logger_dir=str(pathlib.Path(__file__).parent)
    )
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
                logger.info(a)
                logger.info(context.full_path)
        except Exception as e:
            logger.debug(e)


    client.config(
        msg_folder="./tmp/msg",
        logger=logger
    )
    th = client.watch(
        msg_type="processing",
        handler=handler,

    )
    th.join()
except Exception as e:
    logger.debug(e)
