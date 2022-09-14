import bson
import pymongo.database
from enum import Enum
import json
import pymongo
import ReCompact.dbm.DbObjects.Docs
import threading
def __merge__(source, destination):
    """
    run me with nosetests --with-doctest file.py

    >>> a = { 'first' : { 'all_rows' : { 'pass' : 'dog', 'number' : '1' } } }
    >>> b = { 'first' : { 'all_rows' : { 'fail' : 'cat', 'number' : '5' } } }
    >>> merge(b, a) == { 'first' : { 'all_rows' : { 'pass' : 'dog', 'fail' : 'cat', 'number' : '5' } } }
    True
    """
    for key, value in source.items():
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            __merge__(value, node)
        else:
            destination[key] = value
    return destination

def __real_dict_2__(*args,**kwargs):
    ret ={}
    if isinstance(args,tuple) and args.__len__()==1  and isinstance(args[0],dict):
        args=tuple(args[0].items())
    for x in args:
        if isinstance(x,ReCompact.dbm.DbObjects.Docs.Fields):
            m_data=x.to_mongodb()
            item =m_data[ list(m_data.keys())[0]]
            y= __real_dict_2__(m_data)
            if isinstance(item,ReCompact.dbm.Docs.Fields):
                y = __real_dict__(m_data)
            ret =__merge__(y,ret)
            t=ret
        elif isinstance(x,dict):
            k=list(x.keys())[0]
            y = __real_dict__(k,x[k])
            ret =__merge__(y,ret)
        elif isinstance(x,tuple):
            vv = __real_dict__(x[0], x[1])
            ret = __merge__(vv, ret)


        else:
            raise NotImplemented

    return ret
def __real_dict__(data,val=None):




    if isinstance(data,list):
        if data.__len__()==1:
            return {data[0]: val}
        else:
            return {data[0]: __real_dict__(data[1:], val)}
    if isinstance(data,str):
        return __real_dict__(data.split('.'),val)


    elif isinstance(data,dict):
        ret = {}
        next = {}
        for k,v in data.items():
            assert isinstance(k,str)
            items = k.split('.')
            if items.__len__()==1:
                n_v = v
                if isinstance(v, dict):
                    n_v = __real_dict__(v)
                elif isinstance(v,ReCompact.dbm.Docs.Fields):
                    n_v = __real_dict__(v.to_mongodb())
                elif isinstance(v,tuple):
                    n_v = {}
                    for x in v:
                        if isinstance(x,ReCompact.dbm.Docs.Fields):
                            n_v=__merge__(__real_dict__(x.to_mongodb()),n_v)
                ret = __merge__({k:n_v},ret)

            else:
                r_k= ".".join(items[1:])
                n_v=v
                if isinstance(v,dict):
                    n_v = __real_dict__(v)
                elif isinstance(v,ReCompact.dbm.Docs.Fields):
                    m_data = v.to_mongodb()
                    # n_value =m_data[m_data.keys()[0]]
                    m_key =  list(m_data.keys())[0]
                    n_value = m_data[m_key]
                    if isinstance(n_value,dict):
                        n_value= __real_dict__(n_value)

                    n_v = {m_key.split('.')[-1:][0]:n_value}
                r= __real_dict__(items[1:],n_v)

                ret = __merge__( r,ret)



    return ret
class ErrorType(Enum):
    DUPLICATE ="duplicate"
class Error(Exception):
    def __init__(self):
        self.inner_exception=None
        self.error_type =None
        """
        Error Type (Loại lỗi)
        see: ReCompact.dbm.db_actions.ErrorType
        """
        self.db_constraint= None
        """
        Db constraint cause error (ràng buộc database phát sinh lỗi)
        """
        self.message = None

        self.data = None
        """
        Data cause error (dữ liệu gây ra lỗi)
        """
        self.fields=None
        """
        Các field gây ra lỗi
        """
__cache_index_creator__= {}
__lock__ = threading.Lock()
def __get_col__(db:pymongo.database.Database, data_item_type):
    """
    Get Mongodb Collection base on mongodb model
    :param db:
    :param data_item_type:
    :return:
    """
    assert isinstance(data_item_type, type), f"data_item_type must be a type"
    global __cache_index_creator__
    coll_name = data_item_type.__meta__.table_name
    key = f"{db.name}/{coll_name}".lower()


    coll = db.get_collection(coll_name)
    if not __cache_index_creator__.get(key, None):
        __lock__.acquire()
        try:
            if isinstance(data_item_type.__meta__.keys, list):
                for k in data_item_type.__meta__.keys:
                    key_name = k
                    items = k.split(',')
                    indexs = []
                    partialFilterExpression_dict = {}
                    for item in items:
                        indexs.append(
                            (item, pymongo.ASCENDING)
                        )
                        partialFilterExpression_dict = {
                            **partialFilterExpression_dict,
                            **{
                                item:{
                                    "$exists":None
                                }
                            }

                        }
                    try:


                        coll.create_index(
                            indexs,
                            unique=True,
                            sparse= True,
                            # partialFilterExpression =partialFilterExpression_dict,
                            background = True
                        )
                    except:
                        pass
            if isinstance(data_item_type.__meta__.index, list):
                for k in data_item_type.__meta__.index:
                    key_name = k
                    items = k.split(',')
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
            __lock__.release()
            __cache_index_creator__[key] = key
            return coll

    return coll

def __get_all_args_for_insert__(*args, **kwargs):
    import ReCompact.dbm.DbObjects.Docs
    instance = None
    data={}
    if isinstance(args,tuple):
        for v in args:
            if isinstance(v, ReCompact.dbm.DbObjects.Docs.Fields):
                data = __merge__(__real_dict_2__(v.to_mongodb()),data)
                if  isinstance(data.get("Manager",None),tuple):
                    fx=1

            elif isinstance(v,dict):
                data = __merge__(__real_dict_2__(v), data)
            elif isinstance(v,tuple):
                data = __merge__(__real_dict_2__(v), data)
            else:
                instance=v

    if not hasattr(instance, "__db__"):
        raise Exception(f"Please set database "
                        f"Thy must call call variable<<db")
    db = getattr(instance, "__db__")
    coll = __get_col__(db, type(instance))
    return db, instance, coll,data,
def __get_all_args_for_find_one__(*args, **kwargs):
    import ReCompact.dbm.DbObjects.Docs
    instance = args[0]
    filter = args[1]
    if isinstance(filter,ReCompact.dbm.DbObjects.Docs.Fields):
        filter = filter.to_mongodb()
    if not hasattr(instance, "__db__"):
        raise Exception(f"Please set database "
                        f"Thy must call call variable<<db")
    db = getattr(instance, "__db__")
    coll = __get_col__(db, type(instance))
    return db, instance, coll, filter
def __get_all_args_for_find__(*args, **kwargs):
    instance = args[0]
    data = args[1]
    if not hasattr(instance, "__db__"):
        raise Exception(f"Please set database "
                        f"Thy must call call variable<<db")
    db = getattr(instance, "__db__")
    coll = __get_col__(db, type(instance))
    return db, instance, coll, data,


def get_all_args_with_filter(*args, **kwargs):
    instance = args[0]
    filter = args[1]
    data = args[2]

    db = getattr(instance, "__db__")
    coll = __get_col__(db, type(instance))
    return db, instance, coll, filter,__real_dict_2__(data)


def insert_one(*args, **kwargs):
    db, instance, coll, data = __get_all_args_for_insert__(*args, **kwargs)
    assert isinstance(coll, pymongo.database.Collection)
    try:
        ret = coll.insert_one(data)
        data["_id"]=ret._InsertOneResult__inserted_id
        return data

    except pymongo.errors.DuplicateKeyError as e:
        error = Error()
        error.inner_exception = e
        error.message =e._message.split(':')[0]
        error.error_type =ErrorType.DUPLICATE
        str_json= ('{'+e._message.split('{')[1].split('}')[0]+'}').replace('{','{"').replace(': "','": "')
        data_error =json.loads(str_json)
        error.data={}
        for k,v in data_error.items():
            error.data[k.strip(' ')]=v
        error.fields=list(error.data.keys())
        error.db_constraint =e._message.split(':')[1]


        raise error
    except Exception as e:
        error =Error()
        error.inner_exception =e
        raise error



def insert_many(*args, **kwargs):
    # db, instance, coll, data = get_all_args(*args, **kwargs)
    # assert isinstance(coll, pymongo.database.Collection)
    # try:
    #     ret = coll.insert_many(data)
    #     return None, ret
    # except Exception as e:
    #     return e, None
    raise NotImplemented


def update_many(*args, **kwargs):
    db, instance, coll, filter, data = get_all_args_with_filter(*args, **kwargs)
    assert isinstance(coll, pymongo.database.Collection)
    try:
        ret = coll.update_many(filter=filter.to_mongodb(),
                               update=data)
        return ret
    except pymongo.errors.DuplicateKeyError as e:
        error = Error()
        error.inner_exception = e
        error.message = e._message.split(':')[0]
        error.error_type = ErrorType.DUPLICATE
        str_json = ('{' + e._message.split('{')[1].split('}')[0] + '}').replace('{', '{"').replace(': "', '": "')
        data_error = json.loads(str_json)
        error.data = {}
        for k, v in data_error.items():
            error.data[k.strip(' ')] = v
        error.fields = list(error.data.keys())
        error.db_constraint = e._message.split(':')[1]

        raise error


def update_one(*args, **kwargs):
    db, instance, coll, filter, data = get_all_args_with_filter(*args, **kwargs)
    assert isinstance(coll, pymongo.database.Collection)
    try:
        ret = coll.update_many(filter=filter.to_mongodb(),
                               update=data)
        return data
    except pymongo.errors.DuplicateKeyError as e:
        error = Error()
        error.inner_exception = e
        error.message = e._message.split(':')[0]
        error.error_type = ErrorType.DUPLICATE
        str_json = ('{' + e._message.split('{')[1].split('}')[0] + '}').replace('{', '{"').replace(': "', '": "')
        data_error = json.loads(str_json)
        error.data = {}
        for k, v in data_error.items():
            error.data[k.strip(' ')] = v
        error.fields =list(error.data.keys())
        error.db_constraint = e._message.split(':')[1]

        raise error
    except Exception as e:
        error = Error()
        error.inner_exception = e
        raise error


def delete_many(*args, **kwargs):
    import ReCompact.dbm.DbObjects.Docs
    instance = args[0]
    filter = args[1]
    db = instance.__db__
    cls = type(instance)
    coll = db.get_collection(cls.__meta__.table_name)
    assert isinstance(coll, pymongo.collection.Collection)
    if isinstance(filter, ReCompact.dbm.DbObjects.Docs.Fields):
        filter = filter.to_mongodb()
    ret = coll.delete_many(filter)
    return ret


def delete_one(*args, **kwargs):
    import ReCompact.dbm.DbObjects.Docs
    instance=args[0]
    filter = args[1]
    db= instance.__db__
    cls=type(instance)
    coll = db.get_collection(cls.__meta__.table_name)
    assert isinstance(coll,pymongo.collection.Collection)
    if isinstance(filter,ReCompact.dbm.DbObjects.Docs.Fields):
        filter=filter.to_mongodb()
    ret =coll.delete_one(filter)
    return ret



def find_one(*args, **kwargs):
    db, instance, coll, filter = __get_all_args_for_find_one__(*args, **kwargs)
    assert isinstance(coll,pymongo.collection.Collection)
    ret= coll.find_one(filter)
    if ret is None:
        return ret

    return __parse__(ret)


def find(*args, **kwargs):
    db, instance, coll, filter = __get_all_args_for_find_one__(*args, **kwargs)
    assert isinstance(coll,pymongo.database.Collection)
    ret = coll.find(filter)
    for x in ret:
        yield __parse__(x)



def __ob_iter__(*args, **kwargs):
    instance = args[0]
    db = instance.__db__
    coll = __get_col__(db, type(instance))
    assert isinstance(coll, pymongo.collection.Collection)
    if hasattr(instance,"__pipeline__"):
        import ReCompact.dbm.aggregate
        pipeline  = getattr(instance,"__pipeline__")
        instance.__pipeline__ =[]
        curor = coll.aggregate(pipeline)
        for x in curor:
            yield __parse__(x)
    else:
        for x in coll.find({}):
            yield __parse__(x)


def __obj_lshift__(*args, **kwargs):
    if not isinstance(args[1], pymongo.database.Database):
        raise Exception("right argument of left shift must be pymongo.database.Database")
    setattr(args[0], "__db__", args[1])

def __obj_rshift__(*args, **kwargs):
    if not isinstance(args[1], pymongo.database.Database):
        raise Exception("right argument of left shift must be pymongo.database.Database")
    setattr(args[0], "__db__", args[1])

def  __obj_set__(*args,**kwargs):
    import ReCompact.dbm.DbObjects.Docs
    setter = {}
    for x in args:
        if isinstance(x,ReCompact.dbm.DbObjects.Docs.Fields):
            setter ={**setter,**x.to_mongodb()}
        elif isinstance(x,dict):
            setter = {**setter, **x}
    return {"$set":setter}

def __parse__(x):
    ret={}
    for k,v in x.items():
        if isinstance(v,dict):
            v= __parse__(v)
        if isinstance(v,bson.Int64):
            v= int(v)
        ret[k] =v
    return ret