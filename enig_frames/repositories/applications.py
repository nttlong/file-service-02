import enig
import enig_frames.db_context
import api_models.documents
class Applications(enig.Singleton):
    def __init__(self,db=enig.depen(enig_frames.db_context.DbContext)):
        self.db:enig_frames.db_context.DbContext=db
    def create(self, name:str, domain, login_url, description):
        app = self.db.context('admin').find_one(
            docs=api_models.documents.Apps,
            filter=api_models.documents.Apps.NameLower==name.lower()
        )
        if app==None:
            app=self.db.context('admin').insert_one(
                api_models.documents.Apps,
                api_models.documents.Apps.Name==name,
                api_models.documents.Apps.NameLower==name.lower(),
                api_models.documents.Apps.Domain==domain,
                api_models.documents.Apps.Description==description,
                api_models.documents.Apps.LoginUrl==login_url
            )
        return app
    async def create_async(self, name:str, domain, login_url, description):
        app = await self.db.context('admin').find_one_async(
            docs=api_models.documents.Apps,
            filter=api_models.documents.Apps.NameLower==name.lower()
        )
        if app==None:
            app= await self.db.context('admin').insert_one_async(
                api_models.documents.Apps,
                api_models.documents.Apps.Name==name,
                api_models.documents.Apps.NameLower==name.lower(),
                api_models.documents.Apps.Domain==domain,
                api_models.documents.Apps.Description==description,
                api_models.documents.Apps.LoginUrl==login_url
            )
        return app


