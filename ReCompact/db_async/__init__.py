import datetime
import json
import bson
import motor.motor_asyncio
import pymongo
import asyncio
import ReCompact.dbm
import ReCompact.dbm.DbObjects.Docs
import threading
import enum
import quicky.yaml_reader
import pathlib
import os
import pymongo.mongo_client
# from motor import MotorGridFSBucket
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from bson import ObjectId


class PyObjectId(ObjectId):
    """ Custom Type for reading MongoDB IDs """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid object_id")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


import json
from bson import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


__is_has_fix_json__ = False

import bson

__lock__ = threading.Lock()
__cache_index_creator__ = {}
__connection__ = None
db_config = None
default_db_name = None
connection_string = None

if not __is_has_fix_json__:
    __lock__.acquire()
    fn = json.JSONEncoder.default


    def __fix__json__(*args, **kwargs):
        if isinstance(args, tuple) and isinstance(args[1], datetime.datetime):
            return args[1].isoformat()
        if isinstance(args, tuple) and isinstance(args[1], bson.ObjectId):
            v = args[1]
            assert isinstance(v, bson.ObjectId)
            return str(f'"$oid":"{v}"')
        else:
            return fn(*args, **kwargs)


    json.JSONEncoder.default = __fix__json__
    __is_has_fix_json__ = True
    __lock__.release()


def set_default_database(db_name):
    global default_db_name
    default_db_name = db_name


def set_connection_string(str_connection):
    """
    Khởi tạo connection string
    :param str_connection:
    :return:
    """
    global __connection__
    __connection__ = motor.motor_asyncio.AsyncIOMotorClient(str_connection)


def load_config(path_to_yalm_database_config):
    global default_db_name
    global db_config
    global connection_string
    global __connection__
    if not os.path.isfile(path_to_yalm_database_config):
        raise Exception(f"'{path_to_yalm_database_config}' was not found")

    db_config = quicky.yaml_reader.from_file(path_to_yalm_database_config)
    default_db_name = db_config["authSource"]
    str_auth = f'{db_config["username"]}:{db_config["password"]}'
    str_host = None
    if isinstance(db_config["host"], list):
        str_host = ",".join(db_config["host"])
    elif isinstance(db_config["host"], str):
        str_host = f'{db_config["host"]}:{db_config["port"]}'
    if db_config.get("replicaSet", None) is not None:
        connection_string = f'mongodb://{db_config["username"]}:{db_config["password"]}@{str_host}/?authSource={db_config["authSource"]}&replicaSet={db_config["replicaSet"]}'
        __connection__ = motor.motor_asyncio.AsyncIOMotorClient(connection_string)
    else:
        connection_string = f'mongodb://{db_config["username"]}:{db_config["password"]}@{str_host}/?authSource={db_config["authSource"]}'
        __connection__ = motor.motor_asyncio.AsyncIOMotorClient(connection_string)


class ErrorType(enum.Enum):
    NONE = "None"
    DUPLICATE_DATA = "DuplicateData"
    DATA_NOT_FOUND = "DataWasNotFound"
    DATA_REQUIRE = "MissingData"
    SYSTEM = "System"


class Error(Exception):
    def __init__(self):
        self.code = ErrorType.NONE
        self.message = ""
        self.fields = []
        self.key_values = {}
        self.inner_exception = None

    def __repr__(self):
        return f"code:{self.code}\n" \
               f"fields:{','.join(self.fields)}\n" \
               f"message:{self.message}"


def __parse_error__(ex):
    ret = Error()
    if isinstance(ex, pymongo.errors.DuplicateKeyError):
        keyPattern = ex.details.get('keyPattern')
        keyValue = ex.details.get('keyValue')
        fields = list(keyPattern.keys())
        ret.inner_exception = ex
        ret.fields = fields
        ret.key_values = keyValue
        ret.fields = fields
        ret.code = ErrorType.DUPLICATE_DATA
        return ret
    elif isinstance(ex, Exception):
        ret.code = ErrorType.SYSTEM
        ret.message = "system error see inner"
        return ret


def __set_connection__(db):
    global __connection__
    global __lock__
    if __connection__ is None:
        __lock__.acquire()
        try:
            if isinstance(db, pymongo.mongo_client.database.Database):
                username = db.client.options._options["username"]
                password = db.client.options._options["password"]
                replicaSet = db.client.options._options.get("replicaSet", None)
                authSource = db.client.options._options["authSource"]
                # host = list(db.client.HOST)
                str_host = ",".join([f"{x[0]}:{x[1]}" for x in list(db.client.nodes)])
                uri = f'mongodb://{username}:{password}@{str_host}/?authSource={authSource}'
                if replicaSet is not None:
                    uri = f'mongodb://{username}:{password}@{str_host}/?replicaSet={replicaSet}&authSource={authSource}'
                __connection__ = motor.motor_asyncio.AsyncIOMotorClient(uri)
        except Exception as e:
            raise e
        finally:
            __lock__.release()
    return getattr(__connection__, db.name)


def __fix_bson_object_id__(fx):
    if fx is None:
        return None
    ret = {}

    if isinstance(fx,dict):
        for k, v in fx.items():
            if isinstance(v, bson.ObjectId):
                ret = {**ret, **{k: str(v)}}

            elif isinstance(v, dict):
                ret = {**ret, **{k: __fix_bson_object_id__(v)}}
            elif isinstance(v, list):
                lst = list(__fix_bson_object_id_in_list__(v))
                ret = {**ret, **{k: lst}}
            else:
                ret = {**ret, **{k: v}}
        return ret
    else:
        return fx


def __fix_bson_object_id_in_list__(fx):
    lst = []
    for x in fx:
        ret = __fix_bson_object_id__(x)
        yield ret


async def __get_collection__(db, collection_name, keys, index):
    coll = getattr(db, collection_name)
    global __cache_index_creator__
    global __lock__
    key = f"{db.name}/{collection_name}".lower()

    if not __cache_index_creator__.get(key, None):
        __lock__.acquire()
        try:
            index_info = await coll.index_information()

            async def check(key):
                set_key = set(key)
                for k, v in index_info.items():
                    set_key_in_db = set([x[0] for x in v.get('key')])
                    if len(set_key_in_db & set_key) > 0:
                        return True
                return False

            if isinstance(keys, list):
                for k in keys:
                    key_name = k
                    items = k.split(',')
                    is_already = await check(items)
                    if is_already:
                        continue
                    indexs = []
                    partialFilterExpression_dict = {}
                    for item in items:
                        indexs.append(
                            (item, pymongo.ASCENDING)
                        )
                        partialFilterExpression_dict = {
                            **partialFilterExpression_dict,
                            **{
                                item: {
                                    "$exists": None
                                }
                            }

                        }
                    try:

                        coll.create_index(
                            indexs,
                            unique=True,
                            sparse=True,
                            # partialFilterExpression =partialFilterExpression_dict,
                            background=True
                        )
                    except:
                        pass
                    finally:
                        pass

            if isinstance(index, list):
                for k in index:
                    key_name = k
                    items = k.split(',')
                    is_already = await check(items)
                    if is_already:
                        continue
                    indexs = []
                    for item in items:
                        indexs.append(
                            (item, pymongo.ASCENDING)
                        )
                    try:
                        coll.create_index(
                            indexs,
                            background=True
                        )
                    except:
                        pass
                    finally:
                        pass
        finally:
            __cache_index_creator__[key] = key
            __lock__.release()
            return coll

    return coll


async def find_one_async(db: motor.motor_asyncio.AsyncIOMotorDatabase, docs, filter=None):
    """

    :param db:
    :param docs:
    :param filter:
    :return:
    """
    async_db = __set_connection__(db)
    coll = await __get_collection__(
        async_db,
        docs.__dict__["__collection_name__"],
        docs.__dict__["__collection_keys__"],
        docs.__dict__["__collection_index__"]
    )
    if filter is None:
        filter = {}
    _filter = filter
    if isinstance(filter, ReCompact.dbm.DbObjects.Docs.Fields):
        _filter = filter.to_mongodb()
    ret = await coll.find_one(_filter)
    ret_dict = __fix_bson_object_id__(ret)
    return ret_dict


def find_one(db: motor.motor_asyncio.AsyncIOMotorDatabase, docs, filter=None):
    ret = sync(find_one_async(db, docs, filter))
    return ret


async def find_async(db: motor.motor_asyncio.AsyncIOMotorDatabase,
                     docs,
                     filter=None,
                     skip=0,
                     limit=100):
    """

        :param db:
        :param docs:
        :param filter:
        :return:
        """
    async_db = __set_connection__(db)

    coll = await __get_collection__(
        async_db,
        docs.__dict__["__collection_name__"],
        docs.__dict__["__collection_keys__"],
        docs.__dict__["__collection_index__"]
    )

    _filter = filter
    if isinstance(filter, ReCompact.dbm.DbObjects.Docs.Fields):
        _filter = filter.to_mongodb()
    ret_cursor = coll.find(_filter)
    ret = await ret_cursor.skip(skip).to_list(limit)
    # lst = list(__fix_bson_object_id_in_list__(ret))
    return ret


def find(db, docs,
         filter=None,
         skip=0,
         limit=100):
    ret = sync(find_async(db, docs, filter, skip, limit))
    return ret


async def delete_many_async(db, docs, filter):
    async_db = __set_connection__(db)
    coll = await __get_collection__(
        async_db,
        docs.__dict__["__collection_name__"],
        docs.__dict__["__collection_keys__"],
        docs.__dict__["__collection_index__"]
    )
    assert isinstance(coll, motor.motor_asyncio.AsyncIOMotorCollection)
    _filter = {}
    if isinstance(filter, ReCompact.dbm.Docs.Fields):
        _filter = filter.to_mongodb()
    elif isinstance(filter, dict):
        _filter = filter
    else:
        raise Exception("filter must be ReCompact.dbm.Docs.Fields or dict")
    ret = await coll.delete_many(_filter)
    return ret


def delete_many(db, docs, filter):
    return sync(delete_many_async(db, docs, filter))


async def delete_one_async(db, docs, filter):
    async_db = __set_connection__(db)
    coll = await __get_collection__(
        async_db,
        docs.__dict__["__collection_name__"],
        docs.__dict__["__collection_keys__"],
        docs.__dict__["__collection_index__"]
    )
    assert isinstance(coll, motor.motor_asyncio.AsyncIOMotorCollection)
    _filter = {}
    if isinstance(filter, ReCompact.dbm.Docs.Fields):
        _filter = filter.to_mongodb()
    elif isinstance(filter, dict):
        _filter = filter
    else:
        raise Exception("filter must be ReCompact.dbm.Docs.Fields or dict")
    ret = await coll.delete_one(_filter)
    return ret


def delete_one(db, docs, filter):
    return sync(delete_one_async(db, docs, filter))


async def update_one_async(db, docs, filter, *args, **kwargs):
    try:
        async_db = __set_connection__(db)
        coll = await __get_collection__(
            async_db,
            docs.__dict__["__collection_name__"],
            docs.__dict__["__collection_keys__"],
            docs.__dict__["__collection_index__"]
        )
        assert isinstance(coll, motor.motor_asyncio.AsyncIOMotorCollection)
        data = {}
        if isinstance(args, tuple) and len(args) > 0:
            for x in args:
                if isinstance(x, dict):
                    data = {**data, **x}
                elif isinstance(x, ReCompact.dbm.Docs.Fields):
                    data = {**data, **x.to_mongodb()}
        _filter = filter
        if isinstance(filter, ReCompact.dbm.Docs.Fields):
            _filter = filter.to_mongodb()
        ret = await coll.update_one(_filter, data)
        data["_id"] = ret.inserted_id
        return data
    except pymongo.errors.DuplicateKeyError as e:
        r_e = __parse_error__(e)
        raise r_e
    except Exception as e:
        raise e


async def insert_one_async(db, docs, *args, **kwargs):
    try:
        async_db = __set_connection__(db)
        if docs.__dict__.get("__collection_name__", None) is None:
            raise Exception(f"{docs.__module__}.{docs.__name__} is not Mongodb Doc")
        coll = await __get_collection__(
            async_db,
            docs.__dict__["__collection_name__"],
            docs.__dict__["__collection_keys__"],
            docs.__dict__["__collection_index__"]
        )
        assert isinstance(coll, motor.motor_asyncio.AsyncIOMotorCollection)
        data = {}
        if isinstance(args, tuple) and len(args) > 0:
            for x in args:
                if isinstance(x, dict):
                    data = {**data, **x}
                elif isinstance(x, ReCompact.dbm.Docs.Fields):
                    data = {**data, **x.to_mongodb()}

        ret = await coll.insert_one(data)
        data["_id"] = ret.inserted_id
        return data
    except pymongo.errors.DuplicateKeyError as e:
        r_e = __parse_error__(e)
        raise r_e
    except Exception as e:
        raise e


def insert_one(db, docs, *args, **kwargs):
    try:
        sync_db = db.delegate
        coll = ReCompact.dbm.DbObjects.__get_col__(sync_db, docs.__dict__["__collection_name__"])

        data = {}
        if isinstance(args, tuple) and len(args) > 0:
            for x in args:
                if isinstance(x, dict):
                    data = {**data, **x}
                elif isinstance(x, ReCompact.dbm.Docs.Fields):
                    data = {**data, **x.to_mongodb()}

        ret = coll.insert_one(data)
        data["_id"] = ret.inserted_id
        return data
    except pymongo.errors.DuplicateKeyError as e:
        r_e = __parse_error__(e)
        raise r_e
    except Exception as e:
        raise e


async def update_one_async(db, docs, filter, *args, **kwargs):
    try:
        async_db = __set_connection__(db)
        coll = await __get_collection__(
            async_db,
            docs.__dict__["__collection_name__"],
            docs.__dict__["__collection_keys__"],
            docs.__dict__["__collection_index__"]
        )
        assert isinstance(coll, motor.motor_asyncio.AsyncIOMotorCollection)
        data = {}
        _filter = {}
        if isinstance(filter, dict):
            _filter = filter
        elif isinstance(filter, ReCompact.dbm.Docs.Fields):
            _filter = filter.to_mongodb()
        else:
            raise Exception("filter of db_asycn.update_one_async or db_asycn.update_one \n"
                            "must be ReCompact.dbm.Docs.Fields or dict\n"
                            "Example:\n"
                            "update_one_async(db,docs,docs._id=='x',docs.Code=='aa')")
        if isinstance(args, tuple):
            for x in args:
                if isinstance(x, dict):
                    data = {**data, **x}
                elif isinstance(x, ReCompact.dbm.Docs.Fields):
                    data = {**data, **x.to_mongodb()}
                elif isinstance(x, tuple):
                    for y in x:
                        if isinstance(y, dict):
                            data = {**data, **y}
                        elif isinstance(x, ReCompact.dbm.Docs.Fields):
                            data = {**data, **y.to_mongodb()}

        ret = await coll.update_one(_filter, {"$set": data})
        return data
    except pymongo.errors.DuplicateKeyError as e:
        r_e = __parse_error__(e)
        raise r_e
    except Exception as e:
        raise e


def update_one(db, docs, filter, *args, **kwargs):

    try:
        sync_db = db.delegate
        coll = ReCompact.dbm.DbObjects.__get_col__(sync_db, docs.__dict__["__collection_name__"])
        data = {}
        _filter = {}
        if isinstance(filter, dict):
            _filter = filter
        elif isinstance(filter, ReCompact.dbm.Docs.Fields):
            _filter = filter.to_mongodb()
        else:
            raise Exception("filter of db_asycn.update_one_async or db_asycn.update_one \n"
                            "must be ReCompact.dbm.Docs.Fields or dict\n"
                            "Example:\n"
                            "update_one_async(db,docs,docs._id=='x',docs.Code=='aa')")
        if isinstance(args, tuple):
            for x in args:
                if isinstance(x, dict):
                    data = {**data, **x}
                elif isinstance(x, ReCompact.dbm.Docs.Fields):
                    data = {**data, **x.to_mongodb()}
                elif isinstance(x, tuple):
                    for y in x:
                        if isinstance(y, dict):
                            data = {**data, **y}
                        elif isinstance(x, ReCompact.dbm.Docs.Fields):
                            data = {**data, **y.to_mongodb()}
        ret = coll.update_one(_filter, {"$set": data})
        return data
    except pymongo.errors.DuplicateKeyError as e:
        r_e = __parse_error__(e)
        raise r_e
    except Exception as e:
        raise e

    return sync(update_one_async(db, docs, filter, *args, **kwargs))


def sync(*args, **kwargs):
    """
    Khử sync
    :param args:
    :param kwargs:
    :return:
    """
    loop = asyncio.get_event_loop()
    coroutine = args[0]
    ret = loop.run_until_complete(coroutine)
    loop.close()
    return ret


def get_connection() -> motor.motor_asyncio.AsyncIOMotorClient:
    global __connection__
    if __connection__ is None:
        raise Exception(f"Thy shoul call Recompact.db_async.load_config")
    return __connection__


__all_instances_db_context__ = {}
__mongo_db_instance__ = {}
__lock_2__ = threading.Lock()


class Aggregate:
    def __init__(self, db, name, keys, indexes):
        self.db = db
        self.name = name
        self.keys = keys
        self.indexes = indexes
        self.page_size = None
        self.page_index = None

        self.pineline = []

    def project(self, *args, **kwargs):
        pipe = {}
        if isinstance(args, dict):
            pipe = {**pipe, **args}
        elif isinstance(args, ReCompact.dbm.Docs.Fields):
            pipe = {**pipe, **args.to_mongodb()}
        elif isinstance(args, tuple):
            for x in args:
                if isinstance(x, dict):
                    pipe = {**pipe, **x}
                elif isinstance(x, ReCompact.dbm.Docs.Fields):
                    fn = x.to_mongodb()
                    if isinstance(fn, str):
                        pipe = {**pipe, **{fn: 1}}
                    elif isinstance(fn, dict):
                        pipe = {**pipe, **fn}
        else:
            raise Exception("selector must be dict or ReCompact.dbm.Docs.Fields")
        alias = {}
        for k, v in kwargs.items():
            if isinstance(v, dict):
                alias = {**alias, **{k: __parser_dict__(v)}}
            elif isinstance(v, tuple):
                t_alais = {}
                for x in v:
                    if isinstance(x, dict):
                        x = __parser_dict__(x)
                        t_alais = {**t_alais, **{x}}
                    elif isinstance(x, ReCompact.dbm.Docs.Fields):
                        if x.__tree__ is None:
                            t_alais = {**t_alais, **{"$" + x.__name__: 1}}
                        else:
                            t_alais = {**t_alais, **{x.to_mongodb()}}
                    else:
                        t_alais = {**t_alais, **{x: 1}}
                alias = {**alias, **{k: t_alais}}
            elif isinstance(v, ReCompact.dbm.Docs.Fields):
                fx = v.to_mongodb()
                if isinstance(fx, str):
                    alias = {**alias, **{k: "$" + fx}}
                else:
                    alias = {**alias, **{k: fx}}
            else:
                alias = {**alias, **{k: v}}
        pipe = {**pipe, **alias}
        if "_id" not in list(pipe.keys()):
            pipe["_id"] = 0

        self.pineline += [{
            "$project": pipe
        }]
        return self

    def sort(self, *args, **kwargs):
        pipe = {}
        if isinstance(args, ReCompact.dbm.Docs.Fields):
            pipe = {**pipe, **args.to_mongodb()}
        elif isinstance(args, dict):
            pipe = args
        elif isinstance(args, tuple):
            for x in args:
                if isinstance(x, ReCompact.dbm.Docs.Fields):
                    pipe = {**pipe, **x.to_mongodb()}
                elif isinstance(x, dict):
                    pipe = {**pipe, **x}
        self.pineline += [
            {
                "$sort": pipe
            }
        ]
        return self

    def pager(self, page_index, page_size):
        self.page_index = page_index
        self.page_size = page_size
        return self

    def match(self,filter):
        _filter =filter
        if isinstance(filter,ReCompact.dbm.Docs.Fields):
            _filter = filter.to_mongodb()
        elif not isinstance(filter,dict):
            raise Exception("aggregate match require filter with dict or ReCompact.dbm.Docs.Fields")
        self.pineline+=[
            {"$match":_filter}
        ]
        return self

    async def to_list_async(self):
        coll = await __get_collection__(
            self.db,
            self.name,
            self.keys,
            self.indexes
        )
        ret = []
        if self.page_size is not None and self.page_index is not None:
            self.pineline += [{
                "$skip": self.page_index * self.page_size
            }, {
                "$limit": self.page_size
            }]

        async for doc in coll.aggregate(self.pineline):
            ret = ret + [__fix_bson_object_id__(doc)]

        return ret


class DbContext:
    def __init__(self, db_name):
        cnn = get_connection()
        self.db = getattr(cnn, db_name)

    async def find_one_async(self, docs, filter):
        ret = await find_one_async(self.db, docs, filter)
        return ret

    def find_one(self, docs, filter):
        return sync(self.find_one_async(docs, filter))

    async def find_async(self, docs, filter, skip=0, limit=100):
        ret = await find_async(self.db, docs, filter, skip, limit)
        return ret

    def find(self, docs, filter, skip=0, limit=100):
        return sync(self.find_async(docs, filter, skip, limit))

    async def insert_one_async(self, docs, *args, **kwargs):
        ret = await insert_one_async(self.db, docs, *args, **kwargs)
        return ret

    async def update_one_async(self, docs, filter, *args, **kwargs):
        ret = await update_one_async(self.db, docs, filter, *args, **kwargs)
        return ret
    def update_one(self, docs, *args, **kwargs):
        ret = update_one(self.db, docs, *args, **kwargs)
        return ret
    async def delete_one_async(self, docs, filter):
        ret = await delete_one_async(self.db, docs, filter)
        return ret

    def insert_one(self, docs, *args, **kwargs):
        ret = insert_one(self.db, docs, *args, **kwargs)
        return ret

    def aggregate(self, docs) -> Aggregate:
        return Aggregate(
            self.db,
            docs.__dict__["__collection_name__"],
            docs.__dict__["__collection_keys__"],
            docs.__dict__["__collection_index__"]
        )

    def get_grid_fs(self) -> AsyncIOMotorGridFSBucket:
        fs = AsyncIOMotorGridFSBucket(self.db)
        return fs

    def get_file_by_name(self, file_name):
        return self.get_grid_fs().find_one({
            "filename": file_name
        })

    async def get_file_by_id(self, file_id) -> motor.motor_asyncio.AsyncIOMotorGridOut:
        if isinstance(file_id, str):
            file_id = bson.ObjectId(file_id)
        ret = await self.get_grid_fs().open_download_stream(file_id)
        return ret


def get_db_context(db_name) -> DbContext:
    global __all_instances_db_context__
    global __lock_2__
    if __all_instances_db_context__.get(db_name, None) is None:
        __lock_2__.acquire()
        try:
            cntx = DbContext(db_name)
            __all_instances_db_context__[db_name] = cntx
        finally:
            __lock_2__.release()
    return __all_instances_db_context__[db_name]


def __parser_dict__(data):
    if isinstance(data, dict):
        ret = {}
        for k, v in data.items():
            if isinstance(v, ReCompact.dbm.Docs.Fields):
                if v.__tree__ is None:
                    ret = {**ret, **{k: "$" + v.__name__}}
                else:
                    ret = {**ret, **{k: v.to_mongodb()}}
            else:
                ret = {**ret, **{k: __parser_dict__(v)}}
        return ret
    else:
        return data
