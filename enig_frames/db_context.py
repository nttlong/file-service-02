import threading
import api_models.documents
import enig
import enig_frames.config
from ReCompact.db_async import get_db_context, load_config_from_dict
import ReCompact.db_async
__lock__ = threading.Lock()
__cache__ = {}


class DbContext(enig.Singleton):
    def __init__(self, config=enig.depen(enig_frames.config.Configuration)):
        self.configuration: enig_frames.config.Configuration = config
        config.get_value_by_key('db')['port']=int(config.get_value_by_key('db')['port'])
        load_config_from_dict(config.get_value_by_key('db'), enig.get_logger())

    @property
    def admin_db_name(self) -> str:
        return self.configuration.config.admin_db_name
    def context(self,app_name:str)->ReCompact.db_async.DbContext:
        return get_db_context(self.get_db_name(app_name))
    def get_db_name(self, app_name: str):
        global __lock__
        global __cache__
        if app_name == "admin":
            return self.admin_db_name
        else:
            if __cache__.get(app_name.lower()) is None:
                __lock__.acquire()
                try:
                    db = get_db_context(self.admin_db_name)
                    app = db.find_one(
                        docs=api_models.documents.Apps,
                        filter=api_models.documents.Apps.NameLower == app_name.lower()
                    )
                    if app is None:
                        app = db.find_one(
                            docs=api_models.documents.Apps,
                            filter=api_models.documents.Apps.Name == app_name
                        )
                        if app is not None:
                            db.update_one(
                                api_models.documents.Apps,
                                api_models.documents.Apps.Name == app_name,
                                api_models.documents.Apps.NameLower==app_name.lower()
                            )
                    if app is None:
                        return None
                    __cache__[app_name.lower()] = app_name
                finally:
                    __lock__.release()
            return __cache__.get(app_name.lower())
