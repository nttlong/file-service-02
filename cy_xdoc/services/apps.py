from cy_xdoc.repos.base import Base
from cy_xdoc.models.apps import App
class AppServices(Base):
    def __init__(self):
        Base.__init__(self)
    def get_list(self, app_name:str):
        docs = self.expr(App)
        ret=self.db(app_name).doc(App).aggregate().project(
            docs._id>>docs.AppId,
            docs.Name,
            docs.Description
        )
        return ret
