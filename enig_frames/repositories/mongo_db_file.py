import enig
import enig_frames.db_context
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from bson import ObjectId
import api_models.documents


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

