import uuid
from datetime import datetime

import enig
import enig_frames.db_context
import api_models.documents
class Files(enig.Singleton):
    def __init__(self,db=enig.depen(enig_frames.db_context.DbContext)):
        self.db:enig_frames.db_context.DbContext=db

    async def get_item_by_upload_id_async(self, app_name:str, upload_id:str):
        ret= await self.db.context(app_name).find_one_async(
            docs= api_models.documents.Files,
            filter= api_models.documents.Files._id==upload_id
        )
        return ret

    async def delete_by_id_async(self, app_name, upload_id):
        ret = await self.db.context(app_name).delete_one_async(
            docs=api_models.documents.Files,
            filter=api_models.documents.Files._id == upload_id
        )
        return ret

    async def clone_async(self, app_name, UploadId):
        item = await self.db.context(app_name).find_one_async(
            api_models.documents.Files,
            api_models.documents.Files._id == UploadId
        )

        if item is None:
            return None
        item[api_models.documents.Files._id] = str(uuid.uuid4())
        item[api_models.documents.Files.Status]=0
        item[api_models.documents.Files.ThumbFileId] = None
        item[api_models.documents.Files.MainFileId] = None
        item[api_models.documents.Files.OCRFileId] = None
        item[api_models.documents.Files.AvailableThumbs] = []
        await self.db.context(app_name).insert_one_async(
            api_models.documents.Files,
            item
        )
        return item
