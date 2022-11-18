import threading
import typing
import uuid

import gridfs
import pymongo.database

import cy_docs
import cy_kit
from cy_xdoc.services.base import Base
from cy_xdoc.models.files import DocUploadRegister, FsFile, FsChunks
from gridfs import GridIn
import bson

from cy_xdoc.services.file_storage import FileStorageService, FileStorageObject
from gridfs import GridOut


@cy_kit.must_imlement(FileStorageObject)
class MongoDbFileStorage:
    def __init__(self, fs: GridIn,db:pymongo.database.Database):
        self.fs = fs
        self.db =db

    def seek(self, position: int):
        return self.fs.seek(position)

    def get_size(self) -> int:
        return self.fs.length

    def tell(self) -> int:
        return self.fs.tell()

    def read(self, size: int) -> bytes:
        return self.fs.read(size)

    def get_id(self) -> str:
        return str(self.fs._id)

    def push(self, content: bytes, chunk_index: int):
        fs_chunks = self.db.get_collection("fs.chunks")
        fs_chunks.insert_one({
            "_id": bson.objectid.ObjectId(),
            "files_id": self.fs._id,
            "n": chunk_index,
            "data": content
        })
        del content


@cy_kit.must_imlement(FileStorageService)
class MongoDbFileService(Base):
    def create(self, app_name: str, rel_file_path: str, chunk_size: int, size: int) -> MongoDbFileStorage:
        fs = cy_docs.create_file(
            client=self.client,
            db_name=self.db_name(app_name),
            file_name=rel_file_path,
            chunk_size=chunk_size,
            file_size=size
        )
        return MongoDbFileStorage(fs,self.client.get_database(self.db_name(app_name)))

    def get_file_by_name(self, app_name, rel_file_path: str) -> MongoDbFileStorage:
        fs = gridfs.GridFS(self.client.get_database(self.db_name(app_name))).find_one(
            {
                "rel_file_path": rel_file_path
            }
        )
        if fs is None:
            fs = gridfs.GridFS(self.client.get_database(self.db_name(app_name))).find_one(
                {
                    "filename": rel_file_path
                }
            )
            if fs is not None:
                self.client.get_database(self.db_name(app_name)).get_collection("fs.files").update_one(
                    {
                        "_id": fs._id
                    },
                    {
                        "$set": {
                            "rel_file_path": rel_file_path
                        }
                    }
                )

        ret = MongoDbFileStorage(fs,self.client.get_database(self.db_name(app_name)))
        return ret

    def get_file_by_id(self, app_name: str, id: str) -> MongoDbFileStorage:
        fs = cy_docs.get_file(self.client, self.db_name(app_name), bson.ObjectId(id))

        ret = MongoDbFileStorage(fs,self.client.get_database(self.db_name(app_name)))
        return ret

    def delete_files_by_id(self, app_name: str, ids: typing.List[str], run_in_thread: bool):
        def run():
            fs = gridfs.GridFS(self.client.get_database(self.db_name(app_name)))
            for x in ids:
                fs.delete(bson.ObjectId(x))

        if run_in_thread:
            threading.Thread(target=run, args=()).start()
        else:
            run()

    def delete_files(self, app_name, files: typing.List[str], run_in_thread: bool):
        def run():
            fs = gridfs.GridFS(self.client.get_database(self.db_name(app_name)))
            for x in files:
                f = fs.find_one({"rel_file_path": x})
                if f:
                    fs.delete(f._id)

        if run_in_thread:
            threading.Thread(target=run, args=()).start()
        else:
            run()
