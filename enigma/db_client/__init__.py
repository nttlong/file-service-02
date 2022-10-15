import kink.inject
import enigma.loggers
import enigma.config
from ReCompact import db_async
import ReCompact.db_context
@kink.inject
class DbClient:
    def __init__(self,config:enigma.config.AppConfig,logger:enigma.loggers.ELogger):
        self.logger:enigma.loggers.ELogger=logger
        self.config:enigma.config.AppConfig=config

        db_async.load_config_from_dict(
            self.config.get_config('db'),
            self.logger.delegate
        )
    def get_db(self,db_name:str)->db_async.DbContext:
        import pymongo.mongo_client
        pymongo.mongo_client.MongoClient
        if db_name=='admin':
            return db_async.get_db_context(self.config.get_config('admin_db_name'))
        return db_async.get_db_context(db_name)

