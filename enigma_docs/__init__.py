import threading
from typing import TypeVar, Union, Generic
from enigma_docs import __under_fields__
import pymongo.database
from typing import List

T = TypeVar('T')


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


class Document(Generic[T]):
    instance: T

    def __init__(self, client: pymongo.MongoClient = None):

        self.__ins__ = None
        self.client: pymongo.MongoClient = client
        self.__pipe_line__ = []
        self.__meta_doc_name__=None

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
        return __under_fields__.create()

    def ToList(self, db_name: str):
        db = self.client

    def find(self, db_name, filter):
        if self.__meta_doc_name__ is None:
            cls = self.__orig_class__.__args__[0]
            self.__meta_doc_name__ = getattr(cls,"__meta_doc_name__")
        coll=self.client.get_database(db_name).get_collection(
            self.__meta_doc_name__
        )
        import enigma_docs.__under_fields__
        if(isinstance(filter,enigma_docs.__under_fields__.__DynamicField__)):
            return coll.find(filter.to_mongodb())
        if isinstance(filter,dict):
            return coll.find(filter)



def document_name(name: str):
    def wrapper(cls):
        setattr(cls, "__meta_doc_name__", name)
        return cls

    return wrapper


def new_object(cls: T, db: pymongo.database.Database = None) -> Document[T]:
    import __modifier__
    ret_cls = __modifier__.define(cls)
    ret = (ret_cls())
    for k, v in cls.__dict__.items():
        if k[0:2] != "__" and k[-2:] != "__":
            setattr(ret, k, v)
    return ret


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
