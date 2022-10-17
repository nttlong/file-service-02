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
