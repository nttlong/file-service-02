import datetime
import re
import json

import bson


def get_field_expr(x, not_prefix=False):
    import datetime
    t1 = datetime.datetime.now()
    if isinstance(x, Fields):
        if x.__tree__ == None:
            if x.__name__ == None:
                return "this"
            else:
                if not not_prefix:
                    return "$" + x.__name__
                else:
                    return x.__name__
        else:
            return x.__tree__
    elif type(x) == str:
        import expression_parser
        return expression_parser.to_mongobd(x)
    else:
        return x


def compile(expression, *args, **kwargs):
    if isinstance(expression, Fields):
        return get_field_expr(expression)
    if type(expression) == str:
        import expression_parser
        return expression_parser.to_mongobd(expression, *args, **kwargs)
    if isinstance(expression, dict):
        return expression


def get_str(d, t=0):
    x = ""
    for i in range(0, t, 1):
        x += "\t"
    if (isinstance(d, dict)):
        ret = x + "{\n"
        for k, v in d.items():
            ret += x + "\t" + '"' + k + '":' + get_str(v, t + 1) + ",\n"
        ret = ret[0:ret.__len__() - 2]
        ret += "\n\t}"
        return ret
    elif type(d) is list:
        ret = x + "[\n"
        for item in d:
            ret += x + "\t" + get_str(item, t + 1) + ",\n"
        ret = ret[0:ret.__len__() - 2] + x + "\n" + x + "\t" + "]"
        return ret
    elif type(d) is type(re.compile("")):
        return d.pattern
    elif type(d) == str:
        return '"' + d + '"'
    else:
        return d.__str__()


def __convert_colon_to_equal(fx):
    k = list(fx.keys())
    v = fx[k[0]]
    if type(v) in [
        str,
        int,
        bool,
        bson.ObjectId,
        datetime.datetime,
        float
    ]:
        return {
            k[0]: {
                "$eq": v
            }

        }
    else:
        return fx


def __apply__(fn, a, b):
    if type(b) in [str, int, bool, datetime.datetime, bson.ObjectId] and a.__tree__ is None:
        a.__tree__ = {
            a.__name__: {
                fn: b
            }
        }
        return a

    if isinstance(b, Fields):
        left = __convert_colon_to_equal(get_field_expr(a))
        right = __convert_colon_to_equal(get_field_expr(b))

        ret_tree = {
            fn: [left, right]
        }
        setattr(a, "__tree__", ret_tree)

    elif isinstance(b, str):
        ret_tree = {
            fn: [get_field_expr(a), b]
        }
        setattr(a, "__tree__", ret_tree)
    elif isinstance(b, tuple) and b.__len__() > 0:
        _b = b[0]
        _params = []
        for i in range(1, b.__len__(), 1):
            _params.append(b[i])
        import expression_parser
        ret_tree = {
            fn: [get_field_expr(a), expression_parser.to_mongobd(_b, *tuple(_params))]
        }
        setattr(a, "__tree__", ret_tree)
    else:
        left_op = get_field_expr(a)
        if type(b) in [str, int, bool, float, datetime.datetime, bson.ObjectId] and fn == "$ne" and type(
                left_op) == str:
            if left_op[0:1] == "$":
                left_op = left_op[1:]
            ret_tree = {
                left_op: {
                    "$ne": b
                }
            }
        else:
            ret_tree = {
                fn: [get_field_expr(a), b]
            }
        setattr(a, "__tree__", ret_tree)
    return a


def __r_apply__(fn, a, b):
    if isinstance(b, Fields):
        ret_tree = {
            fn: [get_field_expr(b), get_field_expr(a)]
        }
        setattr(a, "__tree__", ret_tree)

    elif type(b) == str:
        ret_tree = {
            fn: [b, get_field_expr(a)]
        }
        setattr(a, "__tree__", ret_tree)
    elif isinstance(b, tuple) and b.__len__() > 0:
        _b = b[0]
        _params = []
        for i in range(1, b.__len__(), 1):
            _params.append(b[i])
        import expression_parser
        ret_tree = {
            fn: [expression_parser.to_mongobd(_b, *tuple(_params)), get_field_expr(a)]
        }
        setattr(a, "__tree__", ret_tree)
    else:
        ret_tree = {
            fn: [b, get_field_expr(a)]
        }
        setattr(a, "__tree__", ret_tree)
    return a


def __get_from_dict__(d, not_use_prefix=True):
    ret = {}
    if isinstance(d, dict):
        for k, v in d.items():
            _k = k
            if isinstance(k, Fields):
                _k = get_field_expr(k, not_use_prefix)
            ret.update({
                _k: __get_from_dict__(v, not_use_prefix)
            })
        return ret
    elif isinstance(d, Fields):
        return get_field_expr(d, not_use_prefix)
        # if d.__dict__.has_key("__alias__"):
        #     return {
        #         d.__dict__["__alias__"]:get_field_expr(d)
        #     }
        # else:
        #     return get_field_expr(d,not_use_prefix)
        # return __get_from_dict__(v,not_use_prefix)
    else:
        return d


class BaseFields(object):
    """
    Ancestor of Mongodb parsable Field
    """

    def __init__(self, data=None, for_filter=False):
        self.__name__ = None
        self.__tree__ = None
        self.__for_filter__ = for_filter
        if isinstance(data, str):
            self.__name__ = data
        else:
            self.__tree__ = data


class Fields(BaseFields):
    """
    Mongodb parable document field example:
    Fields().Amount*Fields().Price will be compile to {'$multiply': ['$Amount', '$Price']}
    """

    def __getattr__(self, item):
        ret_field = None
        if self.__name__ != None:
            ret_field = Fields(self.__name__ + "." + item, self.__for_filter__)
            ret_field.__dict__.update({
                "__parent__": self,
                "__document__": self.__dict__.get("__document__", None)
            })

        else:
            ret_field = Fields(item, self.__for_filter__)
            ret_field.__dict__.update({
                "__parent__": self,
                "__document__": self.__dict__.get("__document__", None)
            })
        if self.__dict__.get("__type__", None) != None:
            # __type__ = self.__dict__.get("__type__").__origin__.__dict__.get(item).__origin__
            ret_field.__dict__.update({
                "__type__": self.__dict__.get("__type__").__origin__.__dict__.get(item)
            })

        return ret_field

    def __str__(self):
        if BaseFields(self) == None:
            return "root"
        if self.__tree__ == None:
            return self.__name__
        else:
            return get_str(self.__tree__)

    def __add__(self, other):
        return __apply__("$add", self, other)

    def __sub__(self, other):
        return __apply__("$subtract", self, other)

    def __mul__(self, other):
        return __apply__("$multiply", self, other)

    def __pow__(self, power, modulo=None):
        return __apply__("$power", self, power)

    def __div__(self, other):
        return __apply__("$divide", self, other)

    def __mod__(self, other):
        return __apply__("$mod", self, other)

    def __eq__(self, other):
        if isinstance(other, list):
            is_all_tuple= True
            r_lst =[]
            for item in other:
                if not isinstance(item,tuple):
                    is_all_tuple= False
                    break
                else:
                    f_r = {}
                    for x in item:
                        r= __real_dict__(x.to_mongodb())
                        f_r=__merge__(r,f_r)
                    r_lst+=[f_r]
            if is_all_tuple:
                self.__tree__ = {
                    self.__name__: r_lst
                }
                return self

        if isinstance(other,tuple):
            f_r={}
            for x in other:
                r= __real_dict__(x.to_mongodb())
                f_r=__merge__(r,f_r)
            self.__tree__ = {
                self.__name__: f_r
            }
            return self
        if self.__tree__ is None: #Còn nguyên thủy chưa xử lý
            self.__tree__ = {
                self.__name__: other
            }
            return self
        if self.__dict__.get("__for_filter__", True):
            if type(other) == str:
                self.__tree__ = {
                    self.__name__: {
                        "$regex": re.compile("^" + get_field_expr(other, True) + "$", re.IGNORECASE)
                    }
                }
                return self
            elif self.__tree__ != None and self.__tree__ != {}:
                self.__tree__ = {
                    "$eq": [self.__tree__, get_field_expr(other, True)]
                }
                return self

            else:
                self.__tree__ = {
                    self.__name__: get_field_expr(other, False)
                }
                return self

        return __apply__("$eq", self, other)

    def __ne__(self, other):

        if type(other) == str:
            self.__tree__ = {
                self.__name__: {"$ne": {
                    "$regex": re.compile("^" + other + "$", re.IGNORECASE)
                }}
            }
            return self
        elif type(other) in [int, float, bool, bson.ObjectId, datetime.datetime]:
            n = self.__name__
            if n[0:1] == "$":
                n = n[1:]
            self.__tree__ = {
                n: {"$ne": other}
            }
            return self
        else:
            self.__tree__ = {
                self.__name__: {"$ne": other}
            }
            return self
        return __apply__("$ne", self, other)

    def __le__(self, other):
        return __apply__("$lte", self, other)

    def __lt__(self, other):
        return __apply__("$lt", self, other)

    def __ge__(self, other):
        return __apply__("$gte", self, other)

    def __gt__(self, other):


        return __apply__("$gt", self, other)

    def __and__(self, other):
        return __apply__("$and", self, other)

    def __or__(self, other):
        return __apply__("$or", self, other)

    def __lshift__(self, other):
        if other is 0:
            ret = Fields()
            ret.__tree__ = get_field_expr(other, True)
            ret.__dict__.update({
                "__alias__": self.__name__
            })
            return ret
        if isinstance(other, dict):
            if self.__dict__.has_key("__origin__") or self.__dict__.has_key("__type__"):
                _other = {}
                for k, v in other.items():
                    if isinstance(k, Fields):
                        if k.__parent__.__origin__ == self.__origin__:
                            f = k.__name__[k.__parent__.__name__.__len__() + 1:k.__name__.__len__()]
                            _other.update({
                                f: v
                            })
                        else:
                            f = get_field_expr(k, True)
                            _other.update({
                                f: v
                            })
                    else:
                        _other.update({
                            k: v
                        })

                doc = self.__dict__.get("__origin__", self.__dict__.get("__type__"))
                if isinstance(doc, tuple):
                    doc = doc[0]
                if isinstance(doc, list):
                    doc = doc[0]
                data = doc.__origin__()
                default = [(k, v[2]) for k, v in data.__dict__.items() if
                           isinstance(v, tuple) and v.__len__() == 3 and v[1] == True]
                required = [(k, v[1]) for k, v in data.__dict__.items() if
                            isinstance(v, tuple) and v.__len__() > 1 and v[1] == True]
                missing = list(
                    set([x[0] for x in required]).difference(set(_other)).difference(set([x[0] for x in required])))
                if missing.__len__() > 0:
                    raise Exception("{0} is missing fields {1}".format(
                        self.__name__, missing
                    ))
                wrong_types = [(k, data.__dict__[k][0], type(v)) for k, v in _other.items() if
                               data.__dict__.has_key(k) and \
                               (not ((type(v) == str and data.__dict__[k][0] == str) or \
                                     (type(v) == data.__dict__[k][0]) or \
                                     (v == None and data.__dict__[k][1] == False) or \
                                     (type(v) == list and type(data.__dict__[k][0]))))]
                if wrong_types.__len__() > 0:
                    raise Exception("{0} in {1} must be {2} not {3}".format(
                        wrong_types[0][0],
                        self.__name__,
                        wrong_types[0][1],
                        wrong_types[0][2]
                    ))
                unkown = list(set(_other).difference(set(data.__dict__)))
                if unkown.__len__() > 0:
                    raise Exception("{0} not in {1}".format(
                        unkown,
                        self.__name__
                    ))
                data.__dict__.update(_other)
                for x in default:
                    if not _other.has_key(x[0]):
                        if callable(x[1]):
                            data.__dict__.update({x[0]: x[1]()})
                        else:
                            data.__dict__.update({x[0]: x[1]})
                import mobject
                ret_obj = mobject.dynamic_object()
                ret_obj.__dict__.update(data.__dict__)
                ret_obj.__dict__.update({
                    "__properties__": doc.__origin__().__dict__
                })
                return ret_obj

            elif self.__dict__.get("__type__", None) != None:
                _type_ = self.__dict__["__type__"]
                if hasattr(_type_, "__origin__"):
                    _type_ = _type_.__origin__
                else:
                    _type_ = _type_()

                def feed(x):
                    for k, v in x.__dict__.items():
                        if isinstance(v[0], object):
                            v = v[0]()
                        elif v.__len__() == 3:
                            if callable(v[2]):
                                v = v[2]()
                            else:
                                v = v[2]
                        else:
                            v = None
                        x.__dict__.update({k: v})
                    return x

                x = feed(_type_)
                return x

                # ret_data =_type_.create()
                # return self.__dict__["__type__"]<<{}
            else:
                import mobject
                return mobject.dynamic_object(other)
        # import expression_parser
        if type(other) == str:
            ret = Fields()
            ret.__tree__ = get_field_expr(other, True)
            ret.__dict__.update({
                "__alias__": self.__name__
            })
            return ret
        elif isinstance(other, set):
            _other = list(other)
            ret_data = {}
            for item in _other:
                if isinstance(item, Fields):
                    right = get_field_expr(item, True)
                    if type(right) == str:
                        ret_data.update({
                            right: 1
                        })
                    elif isinstance(right, dict):
                        ret_data.update({
                            self.__name__: right
                        })

            ret = Fields()
            ret.__tree__ = ret_data
            ret.__dict__.update({
                "__alias__": self.__name__
            })
            return ret
        elif isinstance(other, tuple) and other.__len__() > 0:
            _other = other[0]
            if type(_other) == str:
                _param = tuple([x for x in other if other.index(x) > 0])
                ret = Fields()
                ret.__tree__ = expression_parser.to_mongobd(_other, *_param)
                ret.__dict__.update({
                    "__alias__": self.__name__
                })
                return ret
            elif isinstance(_other, Fields):
                ret_dic = {}
                for item in other:
                    ret_dic.update({
                        get_field_expr(item, True): 1
                    })
                ret = Fields()
                ret.__tree__ = ret_dic
                ret.__dict__.update({
                    "__alias__": self.__name__
                })
                return ret
        elif isinstance(other, list):
            ret_dic = []
            for item in other:
                ret_dic.append(
                    get_field_expr(item, True)
                )
            ret = Fields()
            ret.__tree__ = ret_dic
            ret.__dict__.update({
                "__alias__": self.__name__
            })
            return ret
        elif isinstance(other, Fields):
            other.__dict__.update({
                "__alias__": get_field_expr(self, True)
            })
            return other
        else:
            x = other

    def __call__(self, *args, **kwargs):
        if args.__len__() == 1:
            if self.__name__ != None:
                return Fields(self.__name__ + "." + args[0].__str__())
            else:
                return Fields("this" + self.__name__ + "." + args[0].__str__())
        return None

    def __radd__(self, other):
        return __r_apply__("$add", self, other)

    def __ror__(self, other):
        return __r_apply__("$or", self, other)

    def __rand__(self, other):
        return __r_apply__("$and", self, other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rsub__(self, other):
        return __r_apply__("$subtract", self, other)

    def __rdiv__(self, other):
        return __r_apply__("$divide", self, other)

    def __rmod__(self, other):
        return __r_apply__("$mod", self, other)

    def __rpow__(self, other):
        return __r_apply__("$pow", self, other)

    def __set__(self, instance, value):
        x = 1

    def __divmod__(self, other):
        x = 1

    def __rshift__(self, other):
        if isinstance(other, dict):
            return {
                get_field_expr(self, True): __get_from_dict__(other)
            }
        elif isinstance(other, Fields):
            return {
                get_field_expr(self, True): get_field_expr(other)
            }
        else:
            return {
                get_field_expr(self, True): other
            }

    def var(self):
        self.__name__ = "$" + self.__name__
        return self

    def asc(self):
        return {
            get_field_expr(self, True): 1
        }

    def desc(self):
        return {
            get_field_expr(self, True): -1
        }

    def __to_mongodb__(self):
        """
        parse to mongodb expression
        :return:
        """
        if self.__dict__.get("__alias__", None):
            if self.__tree__ == None:
                return {
                    self.__dict__["__alias__"]: self.__name__
                }
            elif self.__name__ == None:
                return {
                    self.__dict__["__alias__"]: self.__tree__
                }
            else:
                return {
                    self.__dict__["__alias__"]: {self.__name__: self.__tree__}
                }
        if self.__tree__ == None:
            return self.__name__
        return self.__tree__

    def to_mongodb(self):
        ret = self.__to_mongodb__()
        return ret

    def __repr__(self):
        ret = self.to_mongodb()
        if isinstance(ret, str):
            return ret
        elif isinstance(ret, dict):
            from bson import json_util
            import json
            return json.dumps(ret, default=json_util.default)

    def at(self,number:int):
        self.__index__=number
        if self.__tree__ is None:
            self.__name__=f"{self.__name__}.{number}"
            # self.__tree__=f"{self.__name__}[{number}]"
            return self
        return self




filters = Fields(None, True)
document = Fields()


def fields():
    # type: () -> object
    return Fields()
#-----------------------------------------------
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
        if isinstance(x,Fields):
            m_data=x.to_mongodb()
            item =m_data[ list(m_data.keys())[0]]
            y= __real_dict_2__(m_data)
            if isinstance(item,Fields):
                y = __real_dict__(m_data)
            ret =__merge__(y,ret)
            t=ret
        elif isinstance(x,dict):
            k=list(x.keys())[0]
            y = __real_dict__(k,x[k])
            ret =__merge__(y,ret)
        elif isinstance(x,tuple):
            y = __real_dict__(x[0], x[1])
            ret = __merge__(y, ret)


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
                elif isinstance(v,Fields):
                    n_v = __real_dict__(v.to_mongodb())
                elif isinstance(v,tuple):
                    n_v = {}
                    for x in v:
                        if isinstance(x,Fields):
                            n_v=__merge__(__real_dict__(x.to_mongodb()),n_v)
                ret = __merge__({k:n_v},ret)

            else:
                r_k= ".".join(items[1:])
                n_v=v
                if isinstance(v,dict):
                    n_v = __real_dict__(v)
                elif isinstance(v,Fields):
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