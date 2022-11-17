import cy_docs
import cy_kit
from cy_xdoc.configs import config
from cy_docs import get_doc
from pymongo.mongo_client import MongoClient
from typing import TypeVar

T = TypeVar("T")


class DbContext:
    def __init__(self, db_name: str, client: MongoClient):
        self.client = client
        self.db_name = db_name

    def doc(self, cls: T):
        return cy_docs.context(
            client=self.client,
            cls=cls

        )[self.db_name]


class DbClient:
    def __init__(self):
        self.config = config
        self.client = MongoClient(**config.db.to_dict())
        print("Create connection")


class Base:
    def __init__(self, db_client: DbClient = cy_kit.single(DbClient)):

        self.config = db_client.config
        self.client = db_client.client

    def expr(self, cls: T) -> T:
        return cy_docs.expr(cls)

    def db_name(self, app_name: str):
        if app_name == 'admin':
            return config.admin_db_name
        else:
            return app_name

    def db(self, app_name: str):
        return DbContext(self.db_name(app_name), self.client)

    async def get_file_async(self, app_name: str, file_id):
        return await cy_docs.get_file_async(self.client, self.db_name(app_name), file_id)


