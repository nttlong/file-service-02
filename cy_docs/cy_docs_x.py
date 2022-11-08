"""
cy_docs is library for mongodb document manipulating such as:
1-binary mongodb expression builder:
    Example: print(cy_docs.fields.code=='001' and cy_docs.fields.age>18)

find, find_one, find_async, find_one_async
Example:
    client = pymongo.mongo_client.MongoClient(host=..,port=..,..)
    my_doc = cy_docs.get_doc(
        "my-docs",
         client
        )
    ret =my_doc['my-db'].insert_one(cy_docs.fields.code<<'001',cy_docs.fields.age<<32)
    print (ret)
Special:
    ret =my_doc['my-db'].insert_one(cy_docs.fields.code<<'001',cy_docs.fields.age<<32) can be changed
    ret =my_doc['my-db']<<(cy_docs.fields.code<<'001',cy_docs.fields.age<<32)
    find_item =my_doc['my-db'].find_one(cy_docs.fields.code=='001' & cy_docs.fields.age == 32) can be changed
    find_item =my_doc['my-db']@(cy_docs.fields.code=='001' & cy_docs.fields.age == 32) can be changed
    find_items = my_doc['my-db'].find(cy_docs.fields.code!='001' & cy_docs.fields.age < 32) can be changed
    find_items = my_doc['my-db']>>(cy_docs.fields.code!='001' & cy_docs.fields.age < 32) can be changed
"""

import threading


def get_version() -> str:
    return "0.0.1"


import datetime
import json
import uuid
from typing import List, Union
from re import Pattern, IGNORECASE
import bson


def get_mongodb_text(data):
    if isinstance(data, dict):
        ret = {}
        for k, v in data.items():
            ret[k] = get_mongodb_text(v)
        return ret
    elif isinstance(data, List):
        ret = []
        for x in data:
            ret += [get_mongodb_text(x)]
        return ret
    elif isinstance(data, str):
        return data
    elif isinstance(data, datetime.datetime):
        return data
    elif isinstance(data, uuid.UUID):
        return data.__str__()
    elif isinstance(data, int):
        return data
    elif isinstance(data, float):
        return data
    elif isinstance(data, complex):
        return dict(
            imag=data.imag,
            real=data.real
        )
    elif isinstance(data, bson.ObjectId):
        return f"ObjectId({data.__str__()})"
    elif isinstance(data, Pattern):
        if (data.flags & IGNORECASE).value != 0:
            return {"$regex": f"{data.pattern}/i"}
        else:
            return {"$regex": data.pattern}
    elif hasattr(type(data), "__str__"):
        fn = hasattr(type(data), "__str__")
        if callable(fn):
            return data.__str__()
        else:
            return data
    else:
        try:
            ret = data.__str__()
            return ret
        finally:
            return data


class __BaseField__:
    def __init__(self, init_value: Union[str, dict], oprator: str = None):
        self.__field_name__ = None
        self.__data__ = None
        self.__oprator__ = oprator
        if isinstance(init_value, str):
            self.__field_name__ = init_value
        elif isinstance(init_value, dict):
            self.__data__ = init_value
        else:
            raise Exception("init_value must be str or ditc")

    def __getattr__(self, item):
        return self.__dict__.get(item)

    def to_mongo_db(self) -> Union[str, dict]:
        if self.__data__ is not None:
            return self.__data__
        else:
            return self.__field_name__

    def to_mongo_db_expr(self) -> Union[str, dict]:
        if self.__data__ is not None:
            return self.__data__
        else:
            return "$" + self.__field_name__


class Field(__BaseField__):
    def __init__(self, init_value: Union[str, dict], oprator: str = None):
        """
        Init a base field
        :param name:
        """
        __BaseField__.__init__(self, init_value, oprator)
        self.__value__ = None
        self.__has_set_value__ = False
        self.__alias__ = None
        self.__sort__ = 1

    def __lshift__(self, other):
        self.__has_set_value__ = True
        data = {}
        if isinstance(other,tuple):
            for x in other:
                if isinstance(x,Field):
                    if not x.__has_set_value__:
                        raise Exception(f"Thous must set {x.__field_name__}. Example:{x.__field_name__}<<my_value")
                    data[x.__field_name__]=x.__value__
                elif isinstance(x,dict):
                    data = {**data,**x}
                else:
                    raise Exception("Invalid expression")
            self.__value__ = data
        else:
            self.__value__ = other
        return self

    def __getattr__(self, item):
        if isinstance(item, str):
            if item[0:2] == "__" and item[-2:] == "__":
                return __BaseField__.__getattr__(self, item)
            else:
                return Field(f"{self.__field_name__}.{item}")
        else:
            return __BaseField__.__getattr__(self, item)

    def __repr__(self):
        if self.__data__ is not None:
            ret = get_mongodb_text(self.__data__)
            return json.dumps(ret)
        else:
            return self.__field_name__

    # all compare operator
    def __eq__(self, other):
        op = "$eq"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__field_name__: other
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )

    def __ne__(self, other):
        op = "$ne"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__field_name__: {
                    "$ne": other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )

    def __lt__(self, other):
        op = "$lt"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__field_name__: {
                    op: other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )
    def __le__(self, other):
        op = "$lte"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__field_name__: {
                    op: other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )

    def __gt__(self, other):
        op = "$gt"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__field_name__: {
                    op: other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )
    def __ge__(self, other):
        op = "$gte"
        if isinstance(other, Field):
            return Field(
                {
                    op: [
                        self.to_mongo_db_expr(),
                        other.to_mongo_db_expr()
                    ]
                }, op
            )
        elif self.__data__ is None:
            return Field({
                self.__field_name__: {
                    op: other
                }
            }, op)
        else:
            if isinstance(other, Field):
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other.to_mongo_db_expr()
                        ]
                    }, op
                )
            else:
                return Field(
                    {
                        op: [
                            self.to_mongo_db_expr(),
                            other
                        ]
                    }, op
                )
    # all logical
    def __and__(self, other):
        if not isinstance(other, Field):
            raise Exception(f"and operation require 2 Field. While {type(other)}")
        return Field(
            {
                "$and": [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, "$and"
        )

    def __or__(self, other):
        if not isinstance(other, Field):
            raise Exception(f"and operation require 2 Field")
        return Field(
            {
                "$or": [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, "$or"
        )
    def __invert__(self):
      op = "$not"
      if self.__data__ is not None:
            return Field({
                op: self.to_mongo_db_expr()
            }, op)
      else:
          raise Exception("Invalid expression")



    # all math operator:
    def __add__(self, other):
        if isinstance(other, Field):
            return Field({
                "$add": [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, "$add")
        else:
            return Field({
                "$add": [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, "$add")
    def __sub__(self, other):
        op="$sub"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)
    def __mul__(self, other):
        op = "$multiply"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)
    def __truediv__(self, other):
        op="$divide"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)
    def __mod__(self, other):
        op="$mod"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)
    def __pow__(self, power, modulo=None):
        op = "$pow"
        if isinstance(power, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    power.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    power
                ]
            }, op)
    def __floordiv__(self, other):
        op = "$floor"
        if isinstance(other, Field):
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other.to_mongo_db_expr()
                ]
            }, op)
        else:
            return Field({
                op: [
                    self.to_mongo_db_expr(),
                    other
                ]
            }, op)
    # Alias
    def __rshift__(self, other):
        init_data = self.__field_name__
        if self.__field_name__ is None:
            init_data = self.__data__
        if isinstance(other,Field):

            ret= Field(init_data)
            ret.__alias__ =other.__field_name__
            return ret
        elif isinstance(other,str):
            ret = Field(init_data)
            ret.__alias__ = other
            return ret
        else:
            raise Exception(f"Thous can not alias mongodb expression with {type(other)}")
        return self
    def asc(self):
        init_data = self.__field_name__
        if self.__field_name__ is None:
            init_data = self.__data__
        ret = Field(init_data)
        ret.__sort__= 1
        return ret
    def desc(self):
        init_data = self.__field_name__
        if self.__field_name__ is None:
            init_data = self.__data__
        ret = Field(init_data)
        ret.__sort__= -1
        return ret
import pymongo.mongo_client


def to_json_convertable(data):
    if isinstance(data, dict):
        ret = {}
        for k, v in data.items():
            ret[k] = to_json_convertable(v)
        return ret
    elif isinstance(data, List):
        ret = []
        for x in data:
            ret += [to_json_convertable(x)]
        return ret
    elif isinstance(data, bson.ObjectId):
        return data.__str__()
    elif isinstance(data,datetime.datetime):
        return data.isoformat()
    else:
        return data


class DocumentObject(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def to_json_convertable(self):
        return to_json_convertable(self)

    def get(self, key):
        if isinstance(key, Field):
            items = key.__field_name__.split('.')
            ret = self
            for x in items:
                ret = dict.get(ret, x)
                if isinstance(ret, dict):
                    ret = DocumentObject(ret)
                if ret is None:
                    return None

            return ret
        else:
            return dict.get(self, key)

    def __getitem__(self, item):
        return self.get(item)


class ExprBuilder:
    def __getattr__(self, item):
        return Field(item)


fields = ExprBuilder()


class DBDocument:
    def __init__(self, collection: pymongo.collection.Collection):
        self.collection = collection

    def __lshift__(self, other):
        if isinstance(other, tuple):
            insert_dict = {}
            for x in other:
                if isinstance(x, Field):
                    if not x.__has_set_value__:
                        raise Exception(f"Please set value for {x}")
                    else:
                        insert_dict[x.__field_name__] = x.__value__
                else:
                    raise Exception("All element in left shift document must be cy_docs.Field. Example:"
                                    "my_doc = cy_docs.get_doc('my-coll-name',client)"
                                    "test_docs['my-db-name']<<( cy_docs.fields.Code <<'001', cy_docs.fields.Name << 'Name'")
            if insert_dict.get("_id") is None:
                insert_dict["_id"] = bson.ObjectId()
            ret = self.collection.insert_one(insert_dict)

            return ret
        else:
            raise Exception("All element in left shift document must be cy_docs.Field. Example:"
                            "my_doc = cy_docs.get_doc('my-coll-name',client)"
                            "test_docs['my-db-name']<<( cy_docs.fields.Code <<'001', cy_docs.fields.Name << 'Name'")

    def __rshift__(self, other):

        if isinstance(other, dict):
            ret = self.collection.find(other)
        elif isinstance(other, Field):
            ret = self.collection.find(other.to_mongo_db_expr())
        else:
            raise Exception("All element in right shift document must be cy_docs.Field. Example:"
                            "my_doc = cy_docs.get_doc('my-coll-name',client)"
                            "test_docs['my-db-name']>>( cy_docs.fields.MyNumber>1000")

        for x in ret:
            if x is None:
                yield None
            yield DocumentObject(x)

    def __matmul__(self, other):
        if isinstance(other, Field):
            ret_item = self.collection.find_one(other.to_mongo_db_expr())
            if ret_item is None:
                return None
            else:

                return DocumentObject(ret_item)
        elif isinstance(other, dict):
            ret_item = self.collection.find_one(other)
            if ret_item is None:
                return None
            else:
                return DocumentObject(ret_item)
        else:
            raise Exception("Param in Find one must be cy_docs.Field or dict")

    def delete(self, filter):
        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = self.collection.delete_many(_filter)
        return ret

    async def delete_async(self, filter):
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient()
        fx = self.collection
        client.delegate = fx.database.client

        coll = client.get_database(fx.database.name).get_collection(fx.name)
        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = await coll.delete_many(_filter)
        return ret

    async def find_one_async(self, filter):
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient()
        fx = self.collection
        client.delegate = fx.database.client

        coll = client.get_database(fx.database.name).get_collection(fx.name)
        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = await coll.find_one(_filter)
        if ret is None:
            return None
        return DocumentObject(ret)

    async def find_async(self, filter, linmit=10000):
        from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection
        client = AsyncIOMotorClient()
        fx = self.collection
        client.delegate = fx.database.client

        coll: AsyncIOMotorCollection = client.get_database(fx.database.name).get_collection(fx.name)
        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = coll.find(_filter)
        ret_items = []
        for document in await ret.to_list(length=100):
            ret_items += [DocumentObject(document)]
        return ret_items
    def find(self, filter, linmit=10000):


        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = self.collection.find(_filter)

        for document in ret:
            yield DocumentObject(document)
    def find_to_json_convertable(self, filter, linmit=10000):


        _filter = filter
        if isinstance(filter, Field):
            _filter = filter.to_mongo_db_expr()

        ret = self.collection.find(_filter)

        for document in ret:
            yield DocumentObject(document).to_json_convertable()
    async def insert_one_async(self, *args, **kwargs):
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient()
        fx = self.collection
        client.delegate = fx.database.client

        coll = client.get_database(fx.database.name).get_collection(fx.name)
        if isinstance(args, tuple):
            if args.__len__() == 1:
                if isinstance(args[0], dict):
                    for k, v in kwargs:
                        args[0][k] = v
                    if args[0].get("_id") is None:
                        args[0] = bson.ObjectId()
                    ret = await coll.insert_one(args[0])
                    return ret
                elif isinstance(args[0], Field):
                    _fx: Field = args[0]
                    if not _fx.__has_set_value__:
                        raise Exception(
                            f"Please set value for {_fx.__field_name__}. Example: {_fx.__field_name__}<<my_value")
                    data = {
                        _fx.__field_name__: fx.__value__
                    }
                    for k, v in kwargs:
                        data[k] = v
                    if args[0].get("_id") is None:
                        args[0] = bson.ObjectId()
                    ret = await coll.insert_one(data)
                    return ret
            else:
                data = {}
                for x in args:
                    if isinstance(x, Field):
                        if not x.__has_set_value__:
                            raise Exception(
                                f"Please set value for {x.__field_name__}. Exmaple {x.__field_name__}<<my_value")
                        data[x.__field_name__] = x.__value__
                    elif isinstance(x, dict):
                        data = {**data, **x}
                if data.get("_id") is None:
                    data["_id"] = bson.ObjectId()
                ret = await coll.insert_one(data)
                return ret

        print(__file__)
        print(args)
        print(kwargs)
        print(__file__)

    def count(self, filter):
        if isinstance(filter, dict):
            return self.collection.count_documents(filter)
        elif isinstance(filter, Field):
            return self.collection.count_documents(filter.to_mongo_db_expr())

    def update(self,filter,*args,**kwargs):
        _filter ={}
        if isinstance(filter,Field):
            _filter =filter.to_mongo_db_expr()
        updater ={}
        for x in args:
            if isinstance(x,Field):
                if not x.__has_set_value__:
                    raise Exception(f"Thous must set {x.__field_name__} a value. Exmaple: {x.__field_name__}<<my_value")
                updater[x.__field_name__]=x.__value__
            elif isinstance(x,dict):
                updater={**updater,**x}
        updater = {**updater,**kwargs}
        ret= self.collection.update_many(
            filter=_filter,
            update={
                "$set":updater
            }
        )
        return ret
    async def update_async(self,filter,*args,**kwargs):
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient()
        fx = self.collection
        client.delegate = fx.database.client

        coll = client.get_database(fx.database.name).get_collection(fx.name)
        _filter ={}
        if isinstance(filter,Field):
            _filter =filter.to_mongo_db_expr()
        updater ={}
        for x in args:
            if isinstance(x,Field):
                if not x.__has_set_value__:
                    raise Exception(f"Thous must set {x.__field_name__} a value. Exmaple: {x.__field_name__}<<my_value")
                updater[x.__field_name__]=x.__value__
            elif isinstance(x,dict):
                updater={**updater,**x}
        updater = {**updater,**kwargs}
        ret= await coll.update_many(
            filter=_filter,
            update={
                "$set":updater
            }
        )
        return ret

    async def count_async(self, filter):
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient()
        fx = self.collection
        client.delegate = fx.database.client

        coll = client.get_database(fx.database.name).get_collection(fx.name)
        if isinstance(filter, dict):
            return await coll.count_documents(filter)
        elif isinstance(filter, Field):
            return await coll.count_documents(filter.to_mongo_db_expr())

    def aggregate(self):
        return AggregateDocument(self)

class AggregateDocument:
    def __init__(self,owner:DBDocument):
        self.owner=owner
        self.pipeline=[]
    def project(self,*args,**kwargs):

        stage={

        }
        if isinstance(args,Field):
            if args.__alias__ is not None:
                stage[args.__alias__] = args.to_mongo_db_expr()
            elif args.__field_name__ is not None:
                stage[args.__field_name__] = 1
            else:
                raise Exception(f"Thous can not use project stage with {args}")
        for x in args:
            if isinstance(x,Field):
                if x.__alias__ is not None:
                    stage[x.__alias__]=x.to_mongo_db_expr()
                elif x.__field_name__ is not None:
                    stage[x.__field_name__] = 1
                else:
                    raise Exception(f"Thous can not use project stage with {x}")
            elif isinstance(x,dict):
                stage={**stage,**x}
            elif isinstance(x,str):
                stage[x]=1
            else:
                raise Exception(f"Thous can not use project stage with {x}")

        stage={**stage,**kwargs}

        self.pipeline+=[
            {
                "$project":stage
            }
        ]

        return self
    def match(self,filter):
        if isinstance(filter,dict):
            self.pipeline+=[
                {
                    "$match":filter
                }
            ]
        elif isinstance(filter,Field):
            self.pipeline += [
                {
                    "$match": filter.to_mongo_db_expr()
                }
            ]
        return self
    def sort(self,*args,**kwargs):
        stage = {

        }
        if isinstance(args, Field):
            if args.__alias__ is not None:
                stage[args.__alias__] = args.to_mongo_db_expr()
            elif args.__field_name__ is not None:
                stage[args.__field_name__] = args.__sort__
            else:
                raise Exception(f"Thous can not sort stage with {args}")
        for x in args:
            if isinstance(x, Field):
                if x.__alias__ is not None:
                    raise Exception(f"Thous can not sort stage with {x}")
                elif x.__field_name__ is not None:
                    stage[x.__field_name__] = x.__sort__
                else:
                    raise Exception(f"Thous can not sort stage with {x}")

            else:
                raise Exception(f"Thous can not use sort stage with {x}")

        stage = {**stage, **kwargs}

        self.pipeline += [
            {
                "$sort": stage
            }
        ]

        return self
    def skip(self,len:int):
        self.pipeline+=[
            {
                "$skip":len
            }
        ]
        return self
    def limit(self,len:int):
        self.pipeline+=[
            {
                "$limit":len
            }
        ]
        return self
    def __repr__(self):
        ret_pipe=""
        for x in self.pipeline:

            b = to_json_convertable(x)
            ret_pipe+=json.dumps(b)+","
        ret_pipe=ret_pipe[:-1]
        ret=f"db.getCollection('{self.owner.collection.name}').aggregate({ret_pipe})"
        return ret

    def __iter__(self):
        ret = self.owner.collection.aggregate(
            self.pipeline
        )
        for x in ret:
            yield DocumentObject(x)
    def to_json_convertable(self):
        for x in self:
            yield to_json_convertable(x)

__cache_index__ = dict()
__cache_unique__ = dict()
__lock__ = threading.Lock()
class Document:
    def __init__(self, collection_name: str, client: pymongo.mongo_client.MongoClient,indexes=[],unique_keys=[]):
        self.client = client
        self.collection_name = collection_name
        self.indexes= indexes
        self.unique_keys =unique_keys

    def __getitem__(self, item):
        global __cache_index__
        global __cache_unique__
        global __lock__

        coll = self.client.get_database(item).get_collection(
            self.collection_name
        )
        for x in self.unique_keys:
            key=f"{item}.{self.collection_name}.{x}"
            if __cache_unique__.get(key) is None:
                __lock__.acquire()
                try:
                    indexes=[]
                    for y in x.split(','):
                        indexes.append(
                            (y, pymongo.ASCENDING)
                        )
                    coll.create_index(
                        indexes,
                        background=True,
                        unique=True,
                        sparse=True,
                    )
                except Exception as e:
                    pass
                finally:
                    __lock__.release()
                    __cache_unique__[key]=key
        for x in self.indexes:
            key=f"{item}.{self.collection_name}.{x}"
            if __cache_index__.get(key) is None:
                __lock__.acquire()
                try:
                    indexes=[]
                    for y in x.split(','):
                        indexes.append(
                            (y, pymongo.ASCENDING)
                        )
                    coll.create_index(
                        indexes,
                        background=True
                    )
                except Exception as e:
                    pass
                finally:
                    __lock__.release()
                    __cache_index__[key]=key


        return DBDocument(coll)



def get_doc(collection_name: str, client: pymongo.mongo_client.MongoClient, indexes: List[str] = [],
            unique_keys: List[str] = []) -> Document:
    return Document(collection_name, client,indexes=indexes,unique_keys=unique_keys)

class Funcs:
    @staticmethod
    def concat(*args):
        data = {}
        __args =[]
        for x in args:
            if isinstance(x,Field):
                __args+=[x.to_mongo_db_expr()]
            elif hasattr(x,"__str__"):
                __args += [x.__str__()]
            else:
                __args += [f"{x}"]
        data={
            "$concat":__args
        }
        return Field(data,"$concat")

    @staticmethod
    def exists(field):
        if isinstance(field,Field):
            return Field({
                field.__field_name__:{
                    "$exists":True
                }
            })
        elif isinstance(field,str):
            return Field({
                field: {
                    "$exists": True
                }
            })
        else:
            raise Exception(f"exists require cy_docs.fields.<field-name> or str")

    @staticmethod
    def is_null(field):
        if isinstance(field, Field):
            return Field({
                field.__field_name__: None
            })
        elif isinstance(field, str):
            return Field({
                field: None
            })
        else:
            raise Exception(f"exists require cy_docs.fields.<field-name> or str")

    @staticmethod
    def is_not_null(field):
        if isinstance(field, Field):
            return Field({
                field.__field_name__:{"$ne:":None}
            })
        elif isinstance(field, str):
            return Field({
                field: {"$ne:":None}
            })
        else:
            raise Exception(f"exists require cy_docs.fields.<field-name> or str")
    @staticmethod
    def not_exists(field):
        if isinstance(field, Field):
            return Field({
                field.__field_name__: {
                    "$exists": False
                }
            })
        elif isinstance(field, str):
            return Field({
                field: {
                    "$exists": False
                }
            })
        else:
            raise Exception(f"exists require cy_docs.fields.<field-name> or str")

__DbContext__cache__ ={}
__DbContext__cache__lock__ = threading.Lock()
class DbContext(object):
    def __new__(cls, *args, **kw):
        global __DbContext__cache__
        global __DbContext__cache__lock__
        if not hasattr(cls, '_instance'):
            __DbContext__cache__lock__.acquire()
            try:
                orig = super(DbContext, cls)
                cls._instance = orig.__new__(cls)
                cls._instance.__init__(*args, **kw)
                def empty(obj,*a,**b):pass

                setattr(cls,"__init__",empty)
            except Exception as e:
                raise e
            finally:
                __DbContext__cache__lock__.release()
        return cls._instance
def document_define(name:str,indexes:List[str],unique_keys:List[str]):
    def wrapper(cls):
        setattr(cls,"__document_name__",name)
        setattr(cls, "__document_indexes__", indexes)
        setattr(cls, "__document_unique_keys__", unique_keys)
        return cls
    return wrapper
