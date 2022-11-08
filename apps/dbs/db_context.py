import pymongo.mongo_client

import cy_kit
import apps.configs
import cy_docs
from typing import TypeVar
T = TypeVar("~T")
class Docs:
    def __init__(self,clent:pymongo.mongo_client.MongoClient,db_name):
        self.client =clent
        self.db_name = db_name
    def doc(self,cls:T)->T:
        ret = cy_docs.get_doc(
            cls.__document_name__,
            self.client,
            cls.__document_indexes__,
            cls.__document_unique_keys__
        )[self.db_name]
        return ret
class DbContext:
    def __init__(
            self,
            config: cy_kit.single(
                apps.configs.Configs
            )
    ):

        self.config = config
        self.client = pymongo.mongo_client.MongoClient(
            **self.config.source.db.to_dict()
        )

    def db(self, app_name)->Docs:
        if app_name=="admin":
            return Docs(self.client,self.config.source.admin_db_name)
        return  Docs(self.client,app_name)


