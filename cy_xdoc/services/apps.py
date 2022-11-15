import cy_docs
from cy_xdoc.repos.base import Base
from cy_xdoc.models.apps import App
class AppServices(Base):
    def __init__(self):
        Base.__init__(self)
    def get_list(self, app_name:str):
        docs = self.expr(App)
        ret=self.db(app_name).doc(App).aggregate().project(
            docs._id>>cy_docs.fields.AppId,
            docs.name,
            docs.description,
            docs.domain,
            docs.login_url,
            docs.return_url_afterSignIn


        ).sort(
            docs.Name.asc(),
            docs.RegisteredOn.desc()
        )
        return ret


    def get_item(self, app_name, app_get):

        docs = self.expr(App)
        return self.db(app_name).doc(App).aggregate().project(
            docs._id >> cy_docs.fields.AppId,
            docs.name,
            docs.description,
            docs.domain,
            docs.login_url,
            docs.return_url_afterSignIn

        ).match(docs.Name==app_get).first_item()
