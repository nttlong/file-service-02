import cy_docs
from cy_xdoc.configs import config
from cy_docs import get_doc
from pymongo.mongo_client import MongoClient
from typing import TypeVar

T = TypeVar("T")


class DbContext:
    def __init__(self, db_name: str, client: MongoClient):
        self.client = client
        self.db_name = db_name
    def doc(self,cls:T):
        return cy_docs.get_doc(
            client=self.client,
            collection_name= cls.__document_name__,
            indexes= cls.__document_indexes__,
            unique_keys= cls.__document_unique_keys__

        )[self.db_name]


class Base:
    def __init__(self):
        self.config = config
        self.client = MongoClient(**config.db.to_dict())

    def expr(self, cls: T) -> T:
        return cy_docs.expr(T)

    def db_name(self, app_name: str):
        if app_name == 'admin':
            return config.admin_db_name
        else:
            return app_name

    def db(self, app_name: str):
        return DbContext(self.db_name(app_name),self.client)
