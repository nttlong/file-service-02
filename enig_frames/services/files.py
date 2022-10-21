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
    def get_item_by_upload_id(self, app_name: str, upload_id: str):
        return self.repo.get_item_by_upload_id(app_name, upload_id)
    async def delete_by_id_async(self, app_name: str, upload_id: str):
        return await self.repo.delete_by_id_async(app_name, upload_id)

    def update_rel_path(self, app_name, file_id, rel_file_path):
        if self.repo.get_file_system_by_rel_path(
            app_name=app_name,
                rel_file_path=rel_file_path
        ) is None:
            return self.repo.update_rel_path(
                app_name=app_name,
                file_id=file_id,
                rel_file_path=rel_file_path
            )

    def update_file_field(self, app_name, upload_id, field, value):
        return self.repo.update_file_field(
            app_name=app_name,
            upload_id=upload_id,
            field=field,
            value=value
        )

    def update_video_info_by_id(self,
                                app_name:str,
                                upload_id:str,
                                duration,
                                height,
                                width,
                                fps
            ):
        return self.repo.update_video_info_by_id(
            app_name=app_name,
            upload_id=upload_id,
            duration=duration,
            fps=fps,
            width=width,
            height=height
        )