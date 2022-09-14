import os.path

import pymongo
import threading
import zipfile
__info__ = {}
__lock__ =threading.Lock()
def set_info(upload_id:str, data:dict):
    global __info__
    global __lock__
    if __info__.get(upload_id, None) is None:
        __lock__.acquire()
        __info__[upload_id] =data
        __lock__.release()
    else:
        for k,v in data.items():
            __info__[upload_id][k] =v

def get_info(upload_id):
    global __info__
    global __lock__
    if __info__.get(upload_id, None) is None:
        __lock__.acquire()
        __info__[upload_id] = {}
        __lock__.release()
    return __info__[upload_id]


def start(
        app_name:str,
        path_to_file: str,
        upload_id:str,
        db: pymongo.mongo_client.database.Database):
    import ntpath
    import web.settings
    file_name = ntpath.basename(path_to_file)
    temp_dir = file_name.split('.')[0]
    full_dir = os.path.join(web.settings.TEMP_UNZIP_DIR,temp_dir)
    set_info(upload_id,dict(
        status="start"
    ))
    if not os.path.isdir(full_dir):
        os.mkdir(full_dir)
    fx = path_to_file




    th=threading.Thread(
        target=do_unzip_save_to_database,
        args=(
            app_name,
            path_to_file,
            full_dir,
            upload_id,
            db,)
    )
    th.start()


def do_unzip_save_to_database(
        app_name,
        path_to_file,
        unzip_to,
        upload_id,
        db:pymongo.mongo_client.database.Database):
    set_info(upload_id, dict(
        status="unzip"
    ))
    with zipfile.ZipFile(path_to_file, 'r') as zip_ref:
        zip_ref.extractall(unzip_to)
    set_info(upload_id, dict(
        status="upzip_complete"
    ))
    scan_folder(app_name,path_to_file,unzip_to,upload_id,'/',db)


def builk_to_data_base(
        app_name,
        path_to_file,
        unzip_to,
        upload_id,
        rel_file_path,
        file_path,
        db:pymongo.mongo_client.database.Database
):
    import ReCompact.db_context
    import ReCompact.dbm.DbObjects
    import api_models.Model_Files
    import api_models.Model_Container
    import uuid
    import datetime
    ChunkSizeInKB=1024
    NumOfChunks,tail = divmod(os.path.getsize(file_path),ChunkSizeInKB*1024)
    if tail>0:
        NumOfChunks+=1
    fs= ReCompact.db_context.create_mongodb_fs_from_file(
        db=db,
        full_path_to_file=file_path,
        chunk_size=ChunkSizeInKB*1024

    )
    id= str(uuid.uuid4())
    import ntpath
    filename, file_extension = os.path.splitext(ntpath.basename(file_path))
    upload_item= api_models.Model_Files.DocUploadRegister(
        _id= id,
        ServerFileName=f"{id}{file_extension}".lower(),
        RegisterOn=datetime.datetime.now(),
        Status=1,
        SizeInBytes = os.path.getsize(file_path),
        ChunkSizeInKB= ChunkSizeInKB,
        ChunkSizeInBytes =ChunkSizeInKB*1024,
        NumOfChunks=NumOfChunks,
        MainFileId = fs._id,
        FullFileName = rel_file_path.lower(),
        FileName = f"{filename}{file_extension}"

    )
    upload_info = ReCompact.dbm.DbObjects.insert(
        db,
        upload_item
    )

    zip_container = ReCompact.dbm.DbObjects.find_to_object(
        db,
        api_models.Model_Container.ZipContainer,
        ReCompact.dbm.FILTER.UploadId== upload_id
    )
    if not zip_container:
        zip_container= api_models.Model_Container.ZipContainer(
            UploadId= upload_id,
            OriginalFileName = filename,
            CreatedOn = datetime.datetime.now(),
            Files =[]
        )
        ReCompact.dbm.DbObjects.insert(
            db,
            zip_container
        )
    ReCompact.dbm.DbObjects.update(
        db,
        api_models.Model_Container.ZipContainer,
        ReCompact.dbm.FILTER.UploadId == upload_id,
        ReCompact.dbm.PUSH (
            ReCompact.dbm.FIELDS.Files ==  upload_item.DICT
        )

    )

    print(rel_file_path)
    print(file_path)


def scan_folder(
        app_name,
        path_to_file,
        unzip_to,
        upload_id,
        rel_root,
        db:pymongo.mongo_client.database.Database
):
    import web.settings
    for obj in os.listdir(unzip_to):
        obj_path = os.path.join(unzip_to,obj)
        obj_rel_path = os.path.join(rel_root,obj)
        if os.path.isfile(obj_path):
            rel_file_path = obj_path[web.settings.TEMP_UNZIP_DIR.__len__()+1:]
            rel_file_path=rel_file_path.replace('\\','/')
            builk_to_data_base(
                app_name,
                path_to_file,
                unzip_to,
                upload_id,
                rel_file_path,
                obj_path,
                db

            )
            set_info(upload_id,dict(
                status="save_file",
                file=obj_rel_path
            ))
        elif os.path.isdir(obj_path):
            scan_folder(
                app_name,
                path_to_file,
                obj_path,
                upload_id,
                obj,
                db
            )




