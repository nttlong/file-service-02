import threading
from typing import TypeVar, Union, Generic

import bson
import gridfs
import motor.motor_asyncio


import pymongo.database
from typing import List

T = TypeVar('T')

# class DocumentObject(dict):
#     def __init__(self,*args,**kwargs):
#         dict.__init__(self,*args,**kwargs)
#     def get(self, __key):
#         from enigma_docs import __under_fields__
#         if isinstance(__key,__under_fields__.__DynamicField__):
#             items = __key.name.split('.')
#             ret=None
#             for x in items:
#                 ret=self.get(x,None)
#                 if ret is None:
#                     return ret
#                 elif
#             return self.get(__key.name)
def __modify_class___getattr__(cls):
    if hasattr(cls, "__has_modifier__"):
        return cls
    old = getattr(cls, "__getattribute__")
    old_set_attr = getattr(cls, "__setattr__")

    def new_mthd(obj, item):
        if item == "id":
            return obj.__dict__.get("_id")
        else:
            return old(obj, item)

    def __setattr__(obj, key, value):
        if key == "id":
            obj.__dict__["_id"] = value
        else:
            old_set_attr(obj, key, value)

    setattr(cls, "__getattribute__", new_mthd)
    setattr(cls, "__setattr__", __setattr__)
    setattr(cls, "__has_modifier__", True)

class DocumentDict(dict):
    def __init__(self,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
    def get(self, key):
        __key= key
        import enigma_docs.__under_fields__
        if isinstance(key,enigma_docs.__under_fields__.__DynamicField__):
            __key=key.name
        items = __key.split('.')
        ret =self
        for x in items:
            ret=dict.get(ret,x)
            if ret is None:
                return ret
        return ret
    def __getitem__(self, item):
        return self.get(item)

    def to_json_compatible(self):
        def convert(fx):
            if isinstance(fx,bson.ObjectId):
                return str(fx)
            if isinstance(fx,dict):
                ret ={}
                for k,v in fx.items():
                    if isinstance(v,dict):
                        ret[k]=convert(v)
                    elif isinstance(v,List):
                        ret[k]=[]
                        for x in v:
                            ret[k]+=[convert(x)]
                    else:
                        ret[k]=convert(v)
                return ret
            elif isinstance(fx,List):
                ret=[]
                for x in fx:
                    ret+=[convert(x)]
                return ret
            else:
                return fx
        return convert(self)


class Document(Generic[T]):
    instance: T

    def __init__(self, client: pymongo.MongoClient = None):

        self.__ins__ = None
        self.client: pymongo.MongoClient = client
        if isinstance(client,pymongo.MongoClient):
            self.async_client: motor.motor_asyncio.AsyncIOMotorClient = motor.motor_asyncio.AsyncIOMotorClient()
            self.async_client.delegate = self.client
        else:
            self.async_client: motor.motor_asyncio.AsyncIOMotorClient = None

        self.__pipe_line__ = []
        self.__meta_doc_name__ = None

    def __get_client__(self)->pymongo.MongoClient:
        return self.client
    def __get_client_async__(self)->pymongo.MongoClient:
        if self.async_client is None:
            self.async_client = motor.motor_asyncio.AsyncIOMotorClient()
            self.async_client.delegate = self.client
        return self.async_client

    @property
    def object(self) -> T:
        if self.__ins__ is None:
            cls = self.__orig_class__.__args__[0]
            __modify_class___getattr__(cls)
            self.__ins__ = cls()
        return self.__ins__

    @property
    def dict(self) -> dict:
        ret = {}

        def get_value(value):
            import inspect
            if value is None:
                return value
            if isinstance(value, str):
                return value
            if hasattr(value, "__dict__"):
                ret_val = {}
                for k, v in value.__dict__.items():
                    if k[0:2] != "__" and k[-2:] != "__" or k == "_id":
                        if isinstance(v, List):
                            ret_val[k] = []
                            for x in v:
                                ret_val[k] += [get_value(x)]
                        else:
                            ret_val[k] = get_value(v)
                return ret_val
            else:
                return value

        for k, v in self.__ins__.__dict__.items():
            if k[0:2] != "__" and k[-2:] != "__" or k == "_id":
                if isinstance(v, List):
                    ret[k] = []
                    for x in v:
                        ret[k] += [get_value(x)]

                else:
                    ret[k] = get_value(v)
        return ret

    @property
    def fields(self) -> T:
        import enigma_docs.__under_fields__
        return __under_fields__.create()

    def ToList(self, db_name: str):
        db = self.client

    def find(self, db_name, filter={}):
        if self.__meta_doc_name__ is None:
            cls = self.__orig_class__.__args__[0]
            self.__meta_doc_name__ = getattr(cls, "__meta_doc_name__")
        coll = self.client.get_database(db_name).get_collection(
            self.__meta_doc_name__
        )
        import enigma_docs.__under_fields__
        if (isinstance(filter, enigma_docs.__under_fields__.__DynamicField__)):
            return coll.find(filter.to_mongodb())
        if isinstance(filter, dict):
            return coll.find(filter)

    async def find_async(self, db_name, filter={},limit=100)->List:
        if self.__meta_doc_name__ is None:
            cls = self.__orig_class__.__args__[0]
            self.__meta_doc_name__ = getattr(cls, "__meta_doc_name__")
        coll = self.__get_client_async__().get_database(db_name).get_collection(
            self.__meta_doc_name__
        )
        print(f"Collectio ={coll}")
        import enigma_docs.__under_fields__
        if isinstance(filter, enigma_docs.__under_fields__.__DynamicField__):
            cursor = coll.find(filter.to_mongodb())
            print(f"Collectio ={cursor}")
            ret=[]
            for document in await cursor.to_list(length=limit):
                ret += [document]
            return ret

        if isinstance(filter, dict):
            cursor = coll.find(filter.to_mongodb())
            ret = []
            for document in await cursor.to_list(length=limit):
                ret += [document]
            return ret

    def update_one(self, db_name, filter, update):
        if self.__meta_doc_name__ is None:
            cls = self.__orig_class__.__args__[0]
            self.__meta_doc_name__ = getattr(cls, "__meta_doc_name__")
        coll = self.client.get_database(db_name).get_collection(
            self.__meta_doc_name__
        )
        import enigma_docs.__under_fields__
        _filter = filter
        _set = update
        if isinstance(filter, enigma_docs.__under_fields__.__DynamicField__):
            _filter = filter.to_mongodb()
        if isinstance(update,enigma_docs.__under_fields__.__DynamicField__):
            _set = update.to_mongodb()
        ret = coll.update_one(
            filter=_filter,
            update = {
                "$set":_set
            }
        )
        return ret

    def find_one(self, db_name, filter):
        if self.__meta_doc_name__ is None:
            cls = self.__orig_class__.__args__[0]
            self.__meta_doc_name__ = getattr(cls, "__meta_doc_name__")
        coll = self.client.get_database(db_name).get_collection(
            self.__meta_doc_name__
        )
        import enigma_docs.__under_fields__
        if isinstance(filter, enigma_docs.__under_fields__.__DynamicField__):
            ret = list(coll.find(filter.to_mongodb()))
            if ret.__len__() == 0:
                return None
            else:
                return ret[0]
        if isinstance(filter, dict):
            ret = list[coll.find_one(filter)]
            if ret.__len__() == 0:
                return None
            else:
                return ret[0]
    def documents(self,db_name:str,filter={})->List[DocumentDict]:
        items = self.find(db_name,filter)
        for x in items:
            if x is None:
                yield None
            else:
                yield DocumentDict(x)
    def document(self,db_name:str,filter={})->DocumentDict:
        item = self.find_one(db_name,filter)
        if item is None:
            return None
        return DocumentDict(item)




def document_name(name: str):
    def wrapper(cls):
        setattr(cls, "__meta_doc_name__", name)
        return cls

    return wrapper





def factory(client: pymongo.MongoClient):
    def wrapper(cls):
        if isinstance(cls, type):
            for k, v in cls.__annotations__.items():
                setattr(cls, k, v)
            ret = cls()
            for k, v in cls.__annotations__.items():
                ip = v()

                ip.client = client

                setattr(ret, k, ip)
            return ret

    return wrapper

def save_to_file(client:pymongo.MongoClient,db_name:str,file_id:Union[bson.ObjectId,str],to_file:str):
    if isinstance(file_id,str):
        file_id = bson.ObjectId(file_id)
    fs= gridfs.GridFS(client.get_database(db_name))
    file = fs.get(file_id)
    bff = file.read(file.chunk_size)
    with open(to_file, "wb") as outfile:
        # Copy the BytesIO stream to the output file
        outfile.write(bff)
    while bff.__len__()>0:

        bff = file.read(file.chunk_size)
        with open(to_file, "ab") as outfile:
            # Copy the BytesIO stream to the output file
            outfile.write(bff)
    file.close()