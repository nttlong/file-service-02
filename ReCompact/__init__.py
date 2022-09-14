import datetime

import bson

from .dbm import table
from .dbm import field
def document(name:str=None,indexes:list=[],keys:list=[]):
    """
    Caset thees class into Mongodb Documtens
    :param name: Collection name
    :param indexes: index fields
    :param keys: unique index
    :return:
    """
    def inherit_all(cls):
        if isinstance(cls,type):
            base_cls= cls.__base__
            if base_cls==object:
                return cls,[],[]
            cls_meta =None
            if hasattr(cls,"__meta__"):
                cls_meta = getattr(cls,"__meta__")
            cls_keys = []
            cls_index = []
            if cls_meta:
                if hasattr(cls_meta,"key"):
                    cls_keys =getattr(cls_meta,"keys")
                if hasattr(cls_meta,"index"):
                    cls_index =getattr(cls_meta,"index")

            while base_cls!=object:
                if hasattr(base_cls,"__meta__"):
                    base_meta= getattr(base_cls,"__meta__")
                    if hasattr(base_meta,"keys"):
                        keys = getattr(base_meta,"keys")
                        if isinstance(keys,list):
                            cls_keys=cls_keys+keys
                    if hasattr(base_meta,"index"):
                        index = getattr(base_meta,"index")
                        if isinstance(index,list):
                            cls_index=cls_index+index
                for k,v in base_cls.__dict__.items():
                    if k.__len__()>4 and k[0:2]=="__" and k[-2:]=="__":
                        continue
                    else:
                        setattr(cls,k,v)
                base_cls =base_cls.__base__

            return cls,cls_keys,cls_index



    def wrapper(*args,**kwargs):
        cls = args[0]
        _,r_keys,r_index = inherit_all(cls)

        for k,v in cls.__dict__.items():
            if k.__len__()>4 and k[0:2] =="__" and k[-2:]=="__":
                continue
            else:
                if isinstance(v,tuple):
                    f = field()
                    f.data_type =v[0]
                    if len(v)>1:
                        f.is_require = v[1]
                    setattr(cls,k,f)
                elif v in [str,int,bool,datetime.datetime,bson.ObjectId]:
                    f = field()
                    f.data_type = v
                    setattr(cls, k, f)
                elif type(v)==type:
                    f = field()
                    f.data_type = dict
                    setattr(cls, k, f)
            # key_word_args = dict(
            #     table_name = name,
            #     indexes=indexes,
            #     keys = keys
            # )


        ret_cls= table(table_name = name,
                index=indexes+r_index,
                keys = keys+r_keys)(cls)

        return ret_cls

    return wrapper
    # return table(table_name=name,indexes=indexes,keys=keys)