import os.path
import threading
import yaml
import sys
from copy import deepcopy


def container(*args, **kwargs):
    fx = args

    def container_wrapper(cls):
        old_getattr = None
        if hasattr(cls, "__getattribute__"):
            old_getattr = getattr(cls, "__getattribute__")

        def __container__getattribute____(obj, item):
            ret = None
            if item[0:2] == "__" and item[-2] == "__":
                if old_getattr is not None:
                    return old_getattr(obj, item)
                else:
                    ret = cls.__dict__.get(item)

            else:
                ret = cls.__dict__.get(item)
            if ret is None:
                __annotations__ = cls.__dict__.get('__annotations__')
                if isinstance(__annotations__, dict):
                    ret = __annotations__.get(item)
            import inspect
            if inspect.isclass(ret):
                ret = container_wrapper(ret)
                return ret

            return ret

        setattr(cls, "__getattribute__", __container__getattribute____)
        return cls()

    return container_wrapper


__cache_depen__ = {}
__lock_depen__ = threading.Lock()
__cache_yam_dict__ = {}
__cache_yam_dict_lock__ = threading.Lock()


def single(cls, *args, **kwargs):
    key = f"{cls.__module__}/{cls.__name__}"
    ret = None
    if __cache_depen__.get(key) is None:
        # __lock_depen__.acquire()
        try:
            # ret = kink.inject(cls)
            # v = ret(**ret.__init__.__annotations__)
            if hasattr(cls.__init__, "__defaults__"):
                if cls.__init__.__defaults__ is not None:
                    args = {}
                    for k, v in cls.__init__.__annotations__.items():
                        for x in cls.__init__.__defaults__:
                            if type(x) == v:
                                args[k] = x
                    v = cls(**args)
                else:
                    v = cls()
            else:
                v = cls()
            __cache_depen__[key] = v
        except Exception as e:
            raise e
        # finally:
        #     __lock_depen__.release()
    return __cache_depen__[key]


def instance(cls, *args, **kwargs):
    if cls.__init__.__defaults__ is not None:
        args = {}
        for k, v in cls.__init__.__annotations__.items():
            for x in cls.__init__.__defaults__:
                if type(x) == v:
                    args[k] = x
        v = cls(**args)
    else:
        v = cls()
    return v


class VALUE_DICT:
    def __init__(self, data: dict):
        self.__data__ = data

    def __parse__(self, ret):
        if isinstance(ret, dict):
            return VALUE_DICT(ret)
        if isinstance(ret, list):
            ret_list = []
            for x in ret:
                ret_list += {self.__parse__(x)}
        return ret

    def __getattr__(self, item):
        if item[0:2] == "__" and item[-2:] == "__":
            return self.__dict__.get(item)
        ret = self.__data__.get(item)
        if isinstance(ret, dict):
            return VALUE_DICT(ret)
        if isinstance(ret, list):
            ret_list = []
            for x in ret:
                ret_list += {self.__parse__(x)}
            return ret_list
        return ret

    def to_dict(self):
        return self.__data__


def yaml_config(full_path_to_yaml_file: str, apply_sys_args: bool = True):
    if not os.path.isfile(full_path_to_yaml_file):
        raise Exception(f"{full_path_to_yaml_file} was not found")
    if __cache_yam_dict__.get(full_path_to_yaml_file) is None:
        try:
            __cache_yam_dict_lock__.acquire()

            with open(full_path_to_yaml_file, 'r') as stream:
                __config__ = yaml.safe_load(stream)
                if apply_sys_args:
                    __config__ = combine_agruments(__config__)
                __cache_yam_dict__[full_path_to_yaml_file] = VALUE_DICT(__config__)
        finally:
            __cache_yam_dict_lock__.release()

    return __cache_yam_dict__.get(full_path_to_yaml_file)


def convert_to_dict(str_path: str, value):
    items = str_path.split('.')
    if items.__len__() == 1:
        return {items[0]: value}
    else:
        return {items[0]: convert_to_dict(str_path[items[0].__len__() + 1:], value)}


def __dict_of_dicts_merge__(x, y):
    z = {}
    if isinstance(x, dict) and isinstance(y, dict):
        overlapping_keys = x.keys() & y.keys()
        for key in overlapping_keys:
            z[key] = __dict_of_dicts_merge__(x[key], y[key])
        for key in x.keys() - overlapping_keys:
            z[key] = deepcopy(x[key])
        for key in y.keys() - overlapping_keys:
            z[key] = deepcopy(y[key])
        return z
    else:
        return y


def combine_agruments(data):
    ret = {}
    for x in sys.argv:
        if x.split('=').__len__() == 2:
            k = x.split('=')[0]
            if x.split('=').__len__() == 2:
                v = x.split('=')[1]
                c = convert_to_dict(k, v)
                ret = __dict_of_dicts_merge__(ret, c)
            else:
                c = convert_to_dict(k, None)
                ret = __dict_of_dicts_merge__(ret, c)
    ret = __dict_of_dicts_merge__(data, ret)
    return ret


__provider_cache__ = dict()


def provider(interface: type, implement: type):
    global __provider_cache__
    import inspect
    if not inspect.isclass(implement):
        raise Exception(f"implement must be class")
    key = f"{interface.__module__}/{interface.__name__}/{implement.__module__}/{implement.__name__}"
    if __provider_cache__.get(key):
        return __provider_cache__[key]

    def get_module(cls):
        return cls.__module__, cls.__name__

    interface_methods = {}
    for x in interface.__bases__:
        for k, v in x.__dict__.items():
            if k[0:2] != "__" and k[:-2] != "__":
                handler = v
                if not inspect.isclass(handler) and callable(handler):
                    if isinstance(v, classmethod):
                        handler = v.__func__
                    interface_methods[k] = handler
    for k, v in interface.__dict__.items():
        if k[0:2] != "__" and k[:-2] != "__":
            handler = v
            if isinstance(v, classmethod):
                handler = v.__func__
            if not inspect.isclass(handler) and callable(handler):
                interface_methods[k] = handler
    implement_methods = {}

    for k, v in implement.__dict__.items():
        if k[0:2] != "__" and k[:-2] != "__":
            handler = v
            if isinstance(v, classmethod):
                handler = v.__func__
            if not inspect.isclass(handler) and callable(handler):
                implement_methods[k] = v
    interface_method_name_set = set(interface_methods.keys())
    implement_methods_name_set = set(implement_methods.keys())
    miss_name = interface_method_name_set.difference(implement_methods_name_set)
    if miss_name.__len__() > 0:
        importers = {}
        msg = ""
        for x in miss_name:
            fnc_declare = ""
            handler = interface_methods[x]
            for a in handler.__code__.co_varnames:
                m = handler.__annotations__.get(a)
                if m:
                    u, v = get_module(m)
                    if u != int.__module__:
                        importers[u] = v
                    fnc_declare += f"{a}:{m.__name__},"
                else:
                    fnc_declare += f"{a},"
            if fnc_declare != "":
                fnc_declare = fnc_declare[:-1]

            full_fnc_decalre = f"def {x}({fnc_declare})"
            if handler.__annotations__.get("return"):
                u, v = get_module(handler.__annotations__.get("return"))
                if u != int.__module__:
                    importers[u] = v
                full_fnc_decalre += f"->{handler.__annotations__.get('return').__name__}:"
            else:
                full_fnc_decalre += ":"

            msg += f"\n{full_fnc_decalre}\n" \
                   f"\traise NotImplemented"
        for k, v in importers.items():
            msg = f"\nfrom {k} import {v}\n{msg}"
        description = f"Please open file:\n{inspect.getfile(implement)}\n goto \n{implement.__name__} \nthen insert bellow code\n:"
        raise Exception(f"{description}{msg}")
    __provider_cache__[key] = single(implement)
    return __provider_cache__[key]
