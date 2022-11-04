import bson
import pymongo.errors

import enig
import enig_frames.db_context
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from bson import ObjectId
import api_models.documents
import gridfs
import ReCompact.db_context
class MongoFiles(enig.Singleton):
    def __init__(self, db=enig.depen(enig_frames.db_context.DbContext)):
        self.db: enig_frames.db_context.DbContext = db

    def get_grid_fs(self, app_name: str) -> AsyncIOMotorGridFSBucket:
        fs = AsyncIOMotorGridFSBucket(self.db.context(app_name).db)
        return fs

    async def delete_by_rel_path_asycn(self, app_name, rel_path):
        d_fs = await self.db.context(app_name).find_one_async(
            docs=api_models.documents.Fs_File,
            filter=api_models.documents.Fs_File.rel_file_path == rel_path
        )
        if d_fs is not None:
            self.get_grid_fs(app_name).delete(ObjectId(d_fs.get("_id")))

    async def delete_by_id_async(self, app_name, id):
        d_fs = await self.db.context(app_name).find_one_async(
            docs=api_models.documents.Fs_File,
            filter=api_models.documents.Fs_File._id == ObjectId(id)
        )
        if d_fs is not None:
            self.get_grid_fs(app_name).delete(ObjectId(d_fs.get("_id")))

    def upload(self, app_name:str, full_path_to_file:str,rel_file_path:str=None)-> gridfs.grid_file.GridIn:
        ret = ReCompact.db_context.create_mongodb_fs_from_file(
            db=self.db.context(app_name).db.delegate,
            full_path_to_file=full_path_to_file,

        )
        if rel_file_path is not None:
            try:
                self.db.context(app_name).update_one(
                    api_models.documents.Fs_File,
                    api_models.documents.Fs_File._id==ret._id,
                    api_models.documents.Fs_File.rel_file_path==rel_file_path
                )
            except pymongo.errors.DuplicateKeyError as e:
                return ret
        return ret

    async def get_by_id_async(self, app_name, file_id):
        gfs = self.get_grid_fs(app_name)
        if isinstance(file_id, str):
            file_id = bson.ObjectId(file_id)
        ret = await gfs.open_download_stream(file_id)
        return ret

    async def get_by_rel_path_async(self, app_name:str, rel_file_path:str):
        fs = await self.db.context(app_name).find_one_async(
            api_models.documents.Fs_File,
            api_models.documents.Fs_File.rel_file_path==rel_file_path
        )
        if fs is not None:
            ret = await self.get_by_id_async(app_name,fs["_id"])
            return ret

