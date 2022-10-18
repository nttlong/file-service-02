import pathlib
import os
import api_models.documents
import enig
import enig_frames.repositories.files
import enig_frames.services.file_system
import enig.types

class Files(enig.Singleton):
    def __init__(self,
                 repo: enig_frames.repositories.files.Files = enig.depen(
                     enig_frames.repositories.files.Files
                 ),
                 file_system: enig_frames.services.file_system.FileSystem= enig.depen(
                     enig_frames.services.file_system.FileSystem
                 )):
        self.repo: enig_frames.repositories.files.Files = repo
        self.file_system = file_system

    async def get_item_by_upload_id_async(self, app_name: str, upload_id: str):
        return await self.repo.get_item_by_upload_id_async(app_name, upload_id)

    async def delete_by_id_async(self, app_name: str, upload_id: str):
        return await self.repo.delete_by_id_async(app_name, upload_id)

