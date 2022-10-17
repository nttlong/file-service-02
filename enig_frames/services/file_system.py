import enig
import enig_frames.repositories.mongo_db_file


class FileSystem(enig.Singleton):
    def __init__(self,
                 repo: enig_frames.repositories.mongo_db_file.MongoFiles = enig.depen(
                     enig_frames.repositories.mongo_db_file.MongoFiles
                 )):
        self.repo = repo

    async def delete_by_rel_path_asycn(self, app_name: str, rel_path: str):
        return await self.repo.delete_by_rel_path_asycn(app_name, rel_path)
    async def delete_by_id_async(self, app_name: str, id: str):
        return await self.repo.delete_by_id_async(app_name,id)