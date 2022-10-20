import bson

import enig
import enig_frames.repositories.mongo_db_file
import enig_frames.repositories.files

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

    def upload(self, app_name:str, full_path_to_file:str,rel_file_path:str=None):
        return self.repo.upload(
            app_name=app_name,
            full_path_to_file=full_path_to_file,
            rel_file_path = rel_file_path
        )
    async def get_by_id_async(self,app_name:str,file_id):
        return await self.repo.get_by_id_async(app_name,file_id)

    async def get_by_rel_path_async(self,app_name:str,rel_file_path:str):
        return await self.repo.get_by_rel_path_async(app_name,rel_file_path)