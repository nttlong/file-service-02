import uuid

from kink import inject
import enigma.loggers
import enigma.db_client
import api_models.documents
@inject
class Apps:
    def __init__(self,client:enigma.db_client.DbClient,logger:enigma.loggers.ELogger):
        self.logger:enigma.loggers.ELogger=logger
        self.client:enigma.db_client.DbClient = client
    async def create(self,app_name:str):
        db=self.client.get_db(app_name)
        app=await db.find_one_async(
            docs=api_models.documents.Apps,
            filter=api_models.documents.Apps.Name==app_name
        )
        if app is None:
            try:
                ret = await db.insert_one_async(
                    api_models.documents.Apps,
                    api_models.documents.Apps._id==str(uuid.uuid4()),
                    api_models.documents.Apps.Name == app_name,
                    api_models.documents.Apps.Description=="Adminstrator app"

                )
            except Exception as e:
                self.logger.debug(e)