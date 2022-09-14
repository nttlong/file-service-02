import json

import bson
import pymongo.collection


def __get_col__(db, data_item_type):
    """
    Get Mongodb Collection base on mongodb model
    :param db:
    :param data_item_type:
    :return:
    """
    assert isinstance(data_item_type, type), f"data_item_type must be a type"
    import pymongo
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


class Aggregate:
    def __init__(self, *args, **kwargs):
        instance = args[0]
        self.db = instance.__db__
        self.cls = type(instance)
        self.collection_name = type(instance).__meta__.table_name
        self.pipeline = []

    def __repr__(self):
        import json
        return json.dumps(self.pipeline)

    def match(self, filter):
        import ReCompact.dbm.DbObjects.Docs
        if isinstance(filter, ReCompact.dbm.DbObjects.Docs.Fields):
            self.pipeline += [{"$match": filter.to_mongodb()}]
        elif isinstance(filter, dict):
            self.pipeline += [{"$match": filter}]
        else:
            raise Exception("match must be call with ReCompact.dbm.DbObjects.Docs.Fields or dict")
        return self

    @property
    def fields(self):
        import ReCompact.dbm.DbObjects.Docs
        return ReCompact.dbm.DbObjects.Docs.Fields

    def project(self, *args, **kwargs):
        import ReCompact.dbm.DbObjects.Docs
        a = {}
        if isinstance(args, tuple):
            for x in args:
                if isinstance(x, ReCompact.dbm.DbObjects.Docs.Fields):
                    a[x.to_mongodb()] = 1
                elif isinstance(x, str):
                    a[x] = 1
        if isinstance(kwargs, dict):
            for k, v in kwargs.items():
                if isinstance(v, ReCompact.dbm.DbObjects.Docs.Fields):
                    a[k] = v.to_mongodb()
                elif isinstance(x, str):
                    a[x] = 1

        self.pipeline += [{"$project": a}]
        return self

    def sort(self, *args, **kwargs):
        import ReCompact.dbm.DbObjects.Docs
        a = {}
        if isinstance(args, tuple):
            for v in args:
                if isinstance(v, dict):
                    a = {**a, **v}
        self.pipeline += [{"$sort": a}]

        return self

    def __iter__(self):
        coll = __get_col__(self.db, self.cls)
        assert isinstance(coll, pymongo.collection.Collection)
        ret = coll.aggregate(self.pipeline)
        for x in ret:
            yield __parse__(x)



class OwnerAggregate(object):
    def __init__(self, *args, **kwargs):
        instance = args[0]
        self.db = instance.__db__
        self.cls = type(instance)
        self.collection_name = type(instance).__meta__.table_name

        self.owner = instance
        if self.owner.__dict__.get("__pipeline__",None) is None:
            self.owner.__dict__["__pipeline__"] =[]


class SelectAggregate(OwnerAggregate):
    def __call__(self, *args, **kwargs):
        if isinstance(args,tuple):
            import ReCompact.dbm.DbObjects.Docs
            project_pinline = {}
            for x in args:
                if isinstance(x, ReCompact.dbm.Docs.Fields):
                    if x.__tree__ is None:
                        project_pinline[x.__name__] = 1
                elif isinstance(x, str):
                    project_pinline[x] = 1
                elif isinstance(x, tuple) and x.__len__() == 2:
                    if isinstance(x[0], ReCompact.dbm.Docs.Fields) and isinstance(x[1], str):
                        if x[0].__tree__ == None:
                            project_pinline[x[1]] = "$" + x[0].__name__
                        else:
                            project_pinline[x[1]] = "$" + x[0].to_mongodb()
        self.owner.__dict__["__pipeline__"] += [{"$project": project_pinline}]
        return self.owner




class FilterAggregate(OwnerAggregate):


    def __call__(self, *args, **kwargs):
        import ReCompact.dbm.DbObjects.Docs
        project_pinline = {}
        if isinstance(args,tuple):
            for x in args:
                if isinstance(x, ReCompact.dbm.DbObjects.Docs.Fields):
                    project_pinline={**project_pinline,**x.to_mongodb()}
                elif isinstance(x,dict):
                    project_pinline = {**project_pinline, **x}
        self.owner.__dict__["__pipeline__"] += [{"$match": project_pinline}]
        return self.owner




class SortAggregate(OwnerAggregate):

    def __call__(self, *args, **kwargs):
        if isinstance(args, tuple):
            import ReCompact.dbm.DbObjects.Docs
            project_pinline = {}
            for x in args:
               if isinstance(x, dict):
                    project_pinline={**project_pinline,**x}

        self.owner.__dict__["__pipeline__"] += [{"$sort": project_pinline}]
        return self.owner
class SkipAggregate(OwnerAggregate):

    def __call__(self, *args, **kwargs):
        if isinstance(args, tuple):
            self.owner.__dict__["__pipeline__"] += [{"$skip": args[0]}]
        return self.owner

class LimitAggregate(OwnerAggregate):

    def __call__(self, *args, **kwargs):
        if isinstance(args, tuple):
            self.owner.__dict__["__pipeline__"] += [{"$limit": args[0]}]
        return self.owner

def __parse__(x):
    ret={}
    for k,v in x.items():
        if isinstance(v,dict):
            v= __parse__(v)
        if isinstance(v,bson.Int64):
            v= int(v)
        ret[k] =v
    return ret