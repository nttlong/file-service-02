import os

import pymongo.database
from PIL import Image

import ReCompact.db_context
import ReCompact.dbm
import api_models.Model_Files

def parse_size(thumb_sizes: str):
    sizes = thumb_sizes.split(',')
    r_s = []
    for s in sizes:
        try:
            i_s = int(s)
            r_s += [i_s]

        except Exception as e:
            pass
    return r_s


def make_thumb(temp_thumb:str,image_file: str, size: int, app_name:str, upload_id:str):

    thumb_dir = os.path.join(temp_thumb, app_name)
    image = Image.open(image_file)
    h, w = image.size
    thumb_width,thumb_height=size,size
    rate = float(thumb_width / w)
    if h > w:
        rate = float(thumb_height / h)
    nh, nw = rate * h, rate * w
    if not os.path.isdir(thumb_dir):
        os.makedirs(thumb_dir)
    image.thumbnail((nh, nw))
    thumb_file_path = os.path.join(thumb_dir,f"{upload_id}_{size}.webp")
    image.save(thumb_file_path)
    image.close()
    del image
    return thumb_file_path


def save_to_db(file, db: pymongo.database.Database, upload_id):
    pass


def make_thumbs(temp_thumb:str,image_file: str, thumb_sizes: str, db: pymongo.database.Database,app_name:str, upload_id: str):
    sizes = parse_size(thumb_sizes)
    for size in sizes:
        if size > 0:
            file=make_thumb(temp_thumb,image_file, size, app_name, upload_id)
            save_to_db(file,db,upload_id)
            fs = ReCompact.db_context.create_mongodb_fs_from_file(
                db,
                full_path_to_file=file,
                chunk_size=1024 * 1024
            )

            ReCompact.dbm.DbObjects.update(
                db,
                data_item_type=api_models.Model_Files.FsFile,
                filter=ReCompact.dbm.FILTER._id == fs._id,
                updator=ReCompact.dbm.SET(
                    ReCompact.dbm.FIELDS.rel_file_path == f"thumbs/{upload_id}/{size}.webp",
                )
            )
            upload_info= ReCompact.dbm.DbObjects.find_one_to_dict(
                db,
                data_item_type=api_models.Model_Files.DocUploadRegister,
                filter=ReCompact.dbm.FILTER._id==upload_id
            )
            if upload_info is not None:
                at = upload_info.get(api_models.Model_Files.DocUploadRegister.AvailableThumbs.__name__,[])
                at+=[f"thumbs/{upload_id}/{size}.webp"]
                ReCompact.dbm.DbObjects.update(
                    db,
                    data_item_type=api_models.Model_Files.DocUploadRegister,
                    filter=ReCompact.dbm.FILTER._id==upload_id,
                    updator=ReCompact.dbm.SET(
                        ReCompact.dbm.FIELDS.AvailableThumbs == at

                    )
                )

            # os.remove(file)
