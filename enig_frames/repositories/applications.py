import enig
import enig_frames.db_context
import api_models.documents


class Applications(enig.Singleton):
    def __init__(self, db=enig.depen(enig_frames.db_context.DbContext)):
        self.db: enig_frames.db_context.DbContext = db

    def create(self, name: str, domain, login_url, description):
        app = self.db.context('admin').find_one(
            docs=api_models.documents.Apps,
            filter=api_models.documents.Apps.NameLower == name.lower()
        )
        if app == None:
            app = self.db.context('admin').insert_one(
                api_models.documents.Apps,
                api_models.documents.Apps.Name == name,
                api_models.documents.Apps.NameLower == name.lower(),
                api_models.documents.Apps.Domain == domain,
                api_models.documents.Apps.Description == description,
                api_models.documents.Apps.LoginUrl == login_url
            )
        return app

    async def create_async(self, name: str, domain, login_url, description):
        app = await self.db.context('admin').find_one_async(
            docs=api_models.documents.Apps,
            filter=api_models.documents.Apps.NameLower == name.lower()
        )
        if app is None:
            app = await self.db.context('admin').insert_one_async(
                api_models.documents.Apps,
                api_models.documents.Apps.Name == name,
                api_models.documents.Apps.NameLower == name.lower(),
                api_models.documents.Apps.Domain == domain,
                api_models.documents.Apps.Description == description,
                api_models.documents.Apps.LoginUrl == login_url
            )
        return app

    def get_list(self, app_name, page_index, page_size, value_search):
        ret = self.db.context(app_name).aggregate(
            api_models.documents.Apps
        ).project(
            api_models.documents.Apps.Name,
            api_models.documents.Apps.Domain,
            api_models.documents.Apps.LoginUrl,
            api_models.documents.Apps.ReturnUrlAfterSignIn,
            api_models.documents.Apps.Description,
            CreatedOn=api_models.documents.Apps.RegisteredOn,
            AppId=api_models.documents.Apps._id
        ).sort(
            api_models.documents.Apps.RegisteredOn.desc(),
            api_models.documents.Apps.Name.desc(),

        ).pager(
            page_size=page_size,
            page_index=page_index
        )

        return ret.to_list()

    async def get_list_async(self,app_name, page_index, page_size, value_search):
        ret = self.db.context(app_name).aggregate(
            api_models.documents.Apps
        ).project(
            api_models.documents.Apps.Name,
            api_models.documents.Apps.Domain,
            api_models.documents.Apps.LoginUrl,
            api_models.documents.Apps.ReturnUrlAfterSignIn,
            api_models.documents.Apps.Description,
            CreatedOn=api_models.documents.Apps.RegisteredOn,
            AppId=api_models.documents.Apps._id
        ).sort(
            api_models.documents.Apps.RegisteredOn.desc(),
            api_models.documents.Apps.Name.desc(),

        ).pager(
            page_size=page_size,
            page_index=page_index
        )

        return await ret.to_list_async()


    def get_app_by_name(self, app_name:str):
        ret = self.db.context('admin').find_one(
            api_models.documents.Apps,
            api_models.documents.Apps.NameLower==app_name.lower()
        )
        if ret is None:
            ret = self.db.context('admin').find_one(
                api_models.documents.Apps,
                api_models.documents.Apps.Name == app_name
            )
            if ret is not None:
                self.db.context('admin').update_one(
                    api_models.documents.Apps,
                    api_models.documents.Apps.Name == app_name,
                    api_models.documents.Apps.NameLower == app_name.lower()
                )
        return ret

