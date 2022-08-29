import threading
import threading
import pymongo
import os
import yaml
import gridfs
import bson
import pymongo.database
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import io
from gridfs import GridFSBucket
__lock__ = threading.Lock()
__cnn__ = None
__cnns__ = {}


def get_db_connection(
        host: str,
        port: int,
        username: str,
        password: str,
        authSource: str,
        authMechanism: str = "SCRAM-SHA-1",
        replicaSet: str = None

) -> pymongo.mongo_client.MongoClient:
    cnn_key = ";".join([
        ";".join(host),
        str(port),
        username,
        password,
        authSource,
        authMechanism
    ]).lower()
    global __cnn__
    global __cnns__
    if __cnns__.get(cnn_key, None) is None:
        __lock__.acquire()
        try:
            ret_cnn = None
            if replicaSet is not None:
                ret_cnn = pymongo.mongo_client.MongoClient(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    authSource=authSource,
                    authMechanism=authMechanism,
                    replicaSet=replicaSet
                )
            else:
                ret_cnn = pymongo.mongo_client.MongoClient(
                    host=host,
                    port=port,
                    username=username,
                    password=password,
                    authSource=authSource,
                    authMechanism=authMechanism
                )
            __cnns__[cnn_key] = ret_cnn
        except Exception as e:
            raise e
        finally:
            __lock__.release()

    return __cnns__.get(cnn_key)


def get_db(db_name=None) -> pymongo.database.Database:
    global __cnn__
    global __lock__
    import pymongo
    import web.settings
    if db_name == None:
        db_name = web.settings.DATABASES["default"]["NAME"]
    if __cnn__ == None:
        try:
            __lock__.acquire()
            import web.settings
            db_config = web.settings.DATABASES["default"]["CLIENT"]
            if db_config.get("replicaSet", None):
                __cnn__ = pymongo.mongo_client.MongoClient(
                    host=db_config["host"],
                    port=db_config["port"],
                    username=db_config["username"],
                    password=db_config["password"],
                    authSource=db_config["authSource"],
                    authMechanism=db_config["authMechanism"],
                    replicaSet=db_config["replicaSet"]
                )
            else:
                __cnn__ = pymongo.mongo_client.MongoClient(
                    host=db_config["host"],
                    port=db_config["port"],
                    username=db_config["username"],
                    password=db_config["password"],
                    authSource=db_config["authSource"],
                    authMechanism=db_config["authMechanism"]
                )
        except Exception as e:
            raise e
        finally:
            __lock__.release()

    return __cnn__.get_database(db_name)


def db_get_gridfs(db: pymongo.database.Database) -> gridfs.GridFS:
    return gridfs.GridFS(db)


def get_mongodb_file_by_file_name(db: pymongo.database.Database, file_name) -> gridfs.grid_file.GridOut:
    """
    Lấy file grid trong mongodb
    """
    fs= GridFSBucket(db,chunk_size_bytes=1024*1024*10)
    ret = fs.open_download_stream_by_name(
        file_name
    )
    return ret
    # return db_get_gridfs(db).find_one({"filename": file_name})


def get_mongodb_file_by_file_id(db: pymongo.database.Database,
                                file_id: bson.objectid.ObjectId) -> gridfs.grid_file.GridOut:
    """
    Lấy file grid trong mongodb với đường dẫn được chỉ định trong path_to_save (bao gồm cả thên file)

    """
    assert isinstance(file_id, bson.objectid.ObjectId), 'id must be pymongo.bson.objectid.ObjectId'
    fs = GridFSBucket(db,chunk_size_bytes= 4194304 )
    ret = fs.open_download_stream(
        file_id
    )
    return ret

    # return db_get_gridfs(db).get(file_id)


def mongodb_file_create(
        db: pymongo.database.Database,
        file_name: str,
        chunk_size: int,
        file_size: int
) -> gridfs.grid_file.GridIn:
    g = db_get_gridfs(db)
    fs = g.new_file()
    fs.name = file_name
    fs.filename = file_name
    fs.close()
    db.get_collection("fs.files").update_one(
        {
            "_id": fs._id
        },
        {
            "$set": {
                "chunkSize": chunk_size,
                "length": file_size
            }
        }
    )
    return fs


def mongodb_file_add_chunks(
        db: pymongo.database.Database,
        fs_id: bson.ObjectId,
        chunk_index: int,
        data: bytes
):
    if isinstance(fs_id,str):
        fs_id=bson.ObjectId(fs_id)
    assert isinstance(fs_id, bson.ObjectId)
    fs_chunks = db.get_collection("fs.chunks")
    fs_chunks.insert_one({
        "_id": bson.objectid.ObjectId(),
        "files_id": fs_id,
        "n": chunk_index,
        "data": data
    })


def create_mongodb_fs_from_file(
        db: pymongo.database.Database,
        full_path_to_file,
        chunk_size=4194304
) -> gridfs.grid_file.GridIn:
    """
    Tạo file trong mongodb theo noi dung nam trong full_path_to_file
    """
    fs = None
    try:
        dir_path, file_name = os.path.split(full_path_to_file)
        g = db_get_gridfs(db)
        fs = g.new_file()
        fs.name = file_name
        fs.filename = file_name
        fs.close()
        db.get_collection("fs.files").update_one(
            {
                "_id": fs._id
            },
            {
                "$set": {
                    "chunkSize": chunk_size,
                    "length": os.path.getsize(full_path_to_file)
                }
            }
        )
        fs_chunks = db.get_collection("fs.chunks")

        n = 0

        with open(full_path_to_file, 'rb') as r_file:
            read_data = r_file.read(chunk_size)
            while read_data.__len__() > 0:
                fs_chunks.insert_one({
                    "_id": bson.objectid.ObjectId(),
                    "files_id": fs._id,
                    "n": n,
                    "data": read_data
                })
                read_data = r_file.read(chunk_size)
                n = n + 1

    except Exception as e:
        raise e
    finally:
        fs.close()
    return fs


def create_mongodb_fs_from_io_array(
        db: pymongo.database.Database,
        stm: io.BytesIO,
        chunk_size=4194304
) -> gridfs.grid_file.GridIn:
    """
    Tạo file trong mongodb theo noi dung nam trong full_path_to_file
    """
    fs = None
    try:

        g = db_get_gridfs(db)
        fs = g.new_file()
        fs.name = "unknown"
        fs.filename = "unknown"
        fs.close()
        db.get_collection("fs.files").update_one(
            {
                "_id": fs._id
            },
            {
                "$set": {
                    "chunkSize": chunk_size,
                    "length": stm.getbuffer().nbytes
                }
            }
        )
        fs_chunks = db.get_collection("fs.chunks")

        n = 0

        read_data = stm.read(chunk_size)
        while read_data.__len__() > 0:
            fs_chunks.insert_one({
                "_id": bson.objectid.ObjectId(),
                "files_id": fs._id,
                "n": n,
                "data": read_data
            })
            read_data = stm.read(chunk_size)
            n = n + 1

    except Exception as e:
        raise e
    finally:
        fs.close()
    return fs
