import re


def __validate_expr__(a,b):
    # if not a.is_compiler():
    #     raise Exception("Invalid expression")
    # if not isinstance(b, __DynamicField__):
    #     raise Exception("Invalid expression")
    # if not b.is_compiler():
    #     raise Exception("Invalid expression")
    pass

def __resole_expr__(A):
    if isinstance(A,__DynamicField__):
        return A.__to_expr__()
    else:
        return A
def __compiler__(op, a, b):
    fa, fb = __resole_expr__(a), __resole_expr__(b)
    if isinstance(fa, dict) or isinstance(fb, dict):
        return {
            op: [fa, fb]
        }
    if not isinstance(fa, dict) and isinstance(fb, dict):
        return {
            fa: {
                op: fb
            }
        }
    if not isinstance(fa, dict) and not isinstance(fb, dict):
        if op=="$ne":
            if fa is None:
                return {
                    "$and": [
                        {fb: {"$exists": True}},
                        {fb: {"$ne":None}}
                    ]
                }
            if fb is None:
                return {
                    "$and": [
                        {fa: {"$exists": True}},
                        {fa: {"$ne":None}}
                    ]
                }
        if op == "$eq":
            if fa is None and fb is None:
                raise Exception("invalid expression")
            if fa is None and fb is not None:
                return {
                    "$or": [
                        {fb: {"$exists": False}},
                        {fb: None}
                    ]
                }
            if fa is not None and fb is None:
                return {
                    "$or": [
                        {fa: {"$exists": False}},
                        {fa: None}
                    ]
                }
            else:
                return {
                    fa: fb
                }
        else:
            return {
                fa: {
                    op: fb
                }
            }
    if isinstance(fa, dict) and not isinstance(fb, dict):
        return {
            fb: {
                op: fa
            }
        }
def __compiler_math__(op, a, b):
    fa, fb = __resole_expr__(a), __resole_expr__(b)
    if  isinstance(fa,str):
        fa="$"+fa
    if  isinstance(fb,str):
        fb="$"+fb
    return {
        op: [fa, fb]
    }


def __check_compare_or_logical__(a, b):
    if isinstance(a,__DynamicField__):
        return a.use_compare_or_logical_op
    if isinstance(b,__DynamicField__):
        return a.use_compare_or_logical_op
    return False


def __check_math_op__(a, b):
    if isinstance(a, __DynamicField__):
        return a.use_math_op
    if isinstance(b, __DynamicField__):
        return a.use_math_op
    return False


def __make_logic__(op, a, b):
    ret= __DynamicField__(name=None)
    ret.compiler=__compiler__(op,a,b)
    ret.use_compare_or_logical_op=__check_compare_or_logical__(a,b) or True
    ret.use_math_op = __check_math_op__(a, b)
    return ret





def __make_math__(op, a, b):
    ret = __DynamicField__(name=None)
    ret.compiler = __compiler_math__(op, a, b)
    ret.use_compare_or_logical_op = __check_compare_or_logical__(a, b)
    ret.use_math_op = __check_math_op__(a, b) or True
    return ret

def __warpper_compare_operator__():
    # class FX:
    #     def __le__(self, other):

    def wrapper(cls):
        compare_operator ={
            "__eq__":"$eq",
            "__lt__": "$lt",
            "__le__": "$lte",
            "__gt__": "$gt",
            "__ge__": "$gte",
            "__ne__": "$ne",
        }
        def mk(op):
            def call(a,b):
                return __make_logic__(op,a,b)
            return call
        for k,v in compare_operator.items():
            setattr(cls,k,mk(v))

        return cls
    return wrapper
def __warpper_logical_operator__():
    # class FX:
    #     def __le__(self, other):

    def wrapper(cls):
        logical_operator ={
            "__and__":"$and",
            "__or__": "$r",
        }
        def mk(op):
            def call(a,b):
                return __make_logic__(op,a,b)
            return call
        for k,v in logical_operator.items():
            setattr(cls,k,mk(v))

        return cls
    return wrapper





def __warpper_math_operator__(metimethical=None):
    class fx:
        def __mul__(self, other):
            pass
        def __matmul__(self, other):
            pass
        def __truediv__(self, other):
            pass
        def __(self, power, modulo=None):
            pass


    def wrapper(cls):
        math_operator ={
            "__add__":"$add",
            "__sub__": "$subtract",
            "__mul__":"$multiply",
            "__truediv__":"$divide",
            "__mod__":"$mod",
            "__pow__":"$pow"
        }
        def mk(op):
            def call(a,b):
                return __make_math__(op,a,b)
            return call
        for k,v in math_operator.items():
            setattr(cls,k,mk(v))

        return cls
    return wrapper

@__warpper_compare_operator__()
@__warpper_logical_operator__()
@__warpper_math_operator__()
class __DynamicField__:

    def __init__(self,name:str):
        self.name=name
        self.compiler=None
        self.use_math_op=False
        self.use_compare_or_logical_op = False
    def __to_expr__(self):
        return self.compiler or self.name

    def __getattr__(self, item):
        return __DynamicField__(f"{self.name}.{item}")
    def __getitem__(self, item):
        if isinstance(item,int):
            return __DynamicField__(
                f"{self.name}[{item}]"
            )
        if isinstance(item,__DynamicField__):
            return __DynamicField__(
                f"{self.name}.{item.name}"
            )
        else:
            raise Exception("Index was not found")
    def __repr__(self):
        import json
        from re import Pattern
        from typing import List
        def __fix_data__(d:dict):
            ret={}
            for k,v in d.items():
                if isinstance(v,Pattern):
                    if (v.flags & re.IGNORECASE).value!=0:
                        ret[k] = {"$regex": f"{v.pattern}/i"}
                    else:
                        ret[k]={"$regex":v.pattern}
                elif isinstance(v,dict):
                    ret[k]=__fix_data__(v)
                elif isinstance(v,List):
                    ret[k] = []
                    for x in v:
                        if isinstance(x,dict):
                            ret[k]+=[__fix_data__(x)]
                        else:
                            ret[k] += [x]
                else:
                    ret[k]=v
            return ret
        data={}
        if self.use_compare_or_logical_op and self.use_math_op:
            data = {
                "$expr":
                self.__to_expr__()
            }
        else:
            data = self.__to_expr__()
        return json.dumps(__fix_data__(data))
    def to_mongodb(self)->dict:
        if self.use_compare_or_logical_op and self.use_math_op:
            return {
                "$expr":
                self.__to_expr__()
            }
        else:
            return  self.__to_expr__()





class __DynamicFields__:
    def __getattr__(self, item):
        return __DynamicField__(item)

def create():
    return __DynamicFields__()