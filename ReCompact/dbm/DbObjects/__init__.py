import asyncio

import ReCompact.dbm


def __get_col__(db, data_item_type):
    """
    Get Mongodb Collection base on mongodb model
    :param db:
    :param data_item_type:
    :return:
    """
    # assert isinstance(data_item_type,type),f"data_item_type must be a type"
    import pymongo
    coll_name = data_item_type
    if isinstance(data_item_type,type):
        coll_name = data_item_type.__meta__.table_name
    coll = db.get_collection(coll_name)
    try:
        if isinstance(data_item_type.__meta__.keys, list):
            for k in data_item_type.__meta__.keys:
                key_name = k
                items = k.split(',')
                indexs = []
                for item in items:
                    indexs.append(
                        (item, pymongo.ASCENDING)
                    )
                coll.create_index(
                    indexs,
                    unique=True
                )
        if isinstance(data_item_type.__meta__.index, list):
            for k in data_item_type.__meta__.index:
                key_name = k
                items = k.split(',')
                indexs = []
                for item in items:
                    indexs.append(
                        (item, pymongo.ASCENDING)
                    )
                coll.create_index(
                    indexs
                )
    finally:
        return coll
    return coll


def update(db, data_item_type, filter, updator):
    import pymongo
    import ReCompact.dbm
    assert isinstance(db, pymongo.mongo_client.database.Database), 'db must be pymongo.mongo_client.database'
    assert isinstance(filter, Docs.Fields), 'filter must be ReCompact.dbm.DbObject.Filter'
    assert type(updator) in [ReCompact.dbm.SET,
                             ReCompact.dbm.PUSH], 'updator must be ReCompact.dbm.SET or ReCompact.dbm.PUSH'
    coll = __get_col__(db, data_item_type)
    ret = coll.update_many(filter.to_mongodb(), updator.to_mongodb())
    return ret


def insert(db, data_item):
    import pymongo
    assert isinstance(db, pymongo.mongo_client.database.Database), 'db must be pymongo.mongo_client.database'
    data_item_type = type(data_item)
    coll = __get_col__(db, data_item_type)
    ret = coll.insert(data_item.__dict__["__fields__"])
    return ret


def find_to_objects(db, data_item_type, filter):
    import pymongo
    assert isinstance(db, pymongo.mongo_client.database.Database), f'db must be pymongo.mongo_client.database.Database'
    assert isinstance(filter, Docs.Fields), 'filter must be ReCompact.dbm.DbObject.Filter'
    coll = __get_col__(db, data_item_type)
    ret = coll.find(filter.to_mongodb())
    for x in list(ret):
        yield data_item_type(x)


def delete(db, data_item_type, filter):
    import pymongo
    assert isinstance(db, pymongo.mongo_client.database.Database), f'db must be pymongo.mongo_client.database.Database'
    assert isinstance(filter, Docs.Fields), 'filter must be ReCompact.dbm.DbObject.Filter'
    coll = __get_col__(db, data_item_type)
    ret = coll.delete_many(filter.to_mongodb())
    return ret


async def find_to_objects_async(db, data_item_type, filter):
    import pymongo
    assert isinstance(db, pymongo.mongo_client.database.Database), f'db must be pymongo.mongo_client.database.Database'
    assert isinstance(filter, Docs.Fields), 'filter must be ReCompact.dbm.DbObject.Filter'
    coll = __get_col__(db, data_item_type)
    ret = coll.find(filter.to_mongodb())
    for x in list(ret):
        yield data_item_type(x)


def find_to_object(db, data_item_type, filter):
    import pymongo
    assert isinstance(db, pymongo.mongo_client.database.Database), f'db must be pymongo.mongo_client.database.Database'
    assert isinstance(filter, Docs.Fields), 'filter must be ReCompact.dbm.DbObject.Filter'
    coll = __get_col__(db, data_item_type)
    ret = coll.find_one(filter.to_mongodb())
    if ret is None:
        return None
    return data_item_type(ret)


def find_to_dict(db, data_item_type, filter):
    import pymongo
    assert isinstance(db, pymongo.mongo_client.database.Database), f'db must be pymongo.mongo_client.database.Database'
    assert isinstance(filter, Docs.Fields), 'filter must be ReCompact.dbm.DbObject.Filter'
    coll = __get_col__(db, data_item_type)
    return coll.find(filter.to_mongodb())


def find_one_to_dict(db, data_item_type, filter):
    import pymongo
    assert isinstance(db, pymongo.mongo_client.database.Database), f'db must be pymongo.mongo_client.database.Database'
    assert isinstance(filter, Docs.Fields), 'filter must be ReCompact.dbm.DbObject.Filter'
    coll = __get_col__(db, data_item_type)
    return coll.find_one(filter.to_mongodb())


def aggregrate(db, object_type):
    return Aggregrate(db, object_type)


from . import Docs

FILTER = Docs.Fields()
FIELDS = Docs.Fields()


class Aggregrate:
    def __init__(self, db, object_type):
        self.db = db
        self.object_type = object_type
        self.mongo_collection = __get_col__(db, object_type)
        self.pipeline = []

    def __iter__(self):
        ret = self.mongo_collection.aggregate(self.pipeline)
        return ret

    def skip(self, number: int):
        self.pipeline.append({
            "$skip": number
        })
        return self

    def limit(self, number: int):
        self.pipeline.append({
            "$limit": number
        })
        return self

    def sort(self, *args, **kwargs):
        _sort = {}
        if isinstance(args, tuple):
            for x in args:
                assert isinstance(x, dict)
                for k, v in x.items():
                    _sort[k] = v
        self.pipeline.append({
            "$sort": _sort
        })
        return self

    def match(self, filter):
        _match = {}
        if isinstance(filter, Docs.Fields):
            self.pipeline.append({
                "$match": filter.to_mongodb()
            })
        elif isinstance(filter, dict):
            self.pipeline.append({
                "$match": filter
            })
        else:
            raise Exception(f"Thy's filter must be ReCompact.dbm.FIELDS or  dict")
        return self
