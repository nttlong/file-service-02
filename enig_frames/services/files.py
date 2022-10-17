import enig
import enig_frames.repositories.files
class Files(enig.Singleton):
    def __init__(self,
                 repo:enig_frames.repositories.files.Files=enig.depen(
                     enig_frames.repositories.files.Files
                 )):
        self.repo: enig_frames.repositories.files.Files = repo
    async def get_item_by_upload_id_async(self,app_name:str, upload_id:str):
        return await self.repo.get_item_by_upload_id_async(app_name, upload_id)

