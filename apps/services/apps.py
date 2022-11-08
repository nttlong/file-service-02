import cy_kit
import apps.dbs.db_context
import apps.models.apps
class AppServices:
    def __init__(
            self,
            db_context=cy_kit.single(
               apps.dbs.db_context.DbContext
            )
    ):
        self.db_context = db_context
    def get_list(self, app_name:str):
        return list(self.db_context.db(app_name).doc(apps.models.apps.App).find_to_json_convertable({}))

