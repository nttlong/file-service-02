import threading
from datetime import datetime
import inspect
import fastapi
import pydantic
import sys

__wrap_pydantic_cache__ = {}
__wrap_pydantic_lock__ = threading.Lock()


def __wrap_pydantic__(pre, cls, is_lock=True):
    global __wrap_pydantic_cache__
    global __wrap_pydantic_lock__
    if __wrap_pydantic_cache__.get(f"{cls.__module__}/{cls.__name__}") and is_lock:
        return __wrap_pydantic_cache__.get(f"{cls.__module__}/{cls.__name__}")
    with __wrap_pydantic_lock__:
        if hasattr(cls,"__origin__"):
            print(cls)
        if hasattr(cls, "__annotations__"):
            ls = list(cls.__dict__.items())
            for k, v in ls:
                if not (k[0:2] == "__" and k[:-2] != "__") and v not in [str, int, datetime, bool,
                                                                         float] and inspect.isclass(v):
                    re_modify = __wrap_pydantic__(cls.__name__, v,False)
                    cls.__annotations__[k] = re_modify
                    setattr(sys.modules[cls.__module__], k, re_modify)

            for k, v in cls.__annotations__.items():
                if v not in [str, int, datetime, bool, float] and inspect.isclass(v):
                    if cls.__annotations__.get(k) is None:
                        re_modify = __wrap_pydantic__(cls.__name__, v)
                        cls.__annotations__[k] = re_modify
                        setattr(sys.modules[cls.__module__], k, re_modify,False)

        ret_cls = type(f"{cls.__name__}", (cls, pydantic.BaseModel,), dict(cls.__dict__))
        setattr(sys.modules[cls.__module__], cls.__name__, ret_cls)
        ret_cls.__name__ = cls.__name__
        __wrap_pydantic_cache__[f"{cls.__module__}/{cls.__name__}"] = ret_cls
    return __wrap_pydantic_cache__.get(f"{cls.__module__}/{cls.__name__}")


def check_is_need_pydantic(cls: type):
    import typing

    if hasattr(cls,"__origin__") and cls.__origin__==typing.List.__origin__ and hasattr(cls,"__args__") and isinstance(cls.__args__,tuple):
        ret=[]
        for x in cls.__args__:
            if check_is_need_pydantic(x):
               ret+=[__wrap_pydantic__("",x,is_lock=False)]
            else:
                ret += [x]
        cls.__args__=tuple(ret)

        return False


    ret = (cls not in [str, int, float, datetime, bool, dict]) and (
                inspect.isclass(cls) and (not issubclass(cls, pydantic.BaseModel)))
    return ret


class __hanlder__:

    def __init__(self, method, path, handler):
        self.path = path
        __old_dfs__ = []
        self.return_type = None
        if handler.__defaults__ is not None:
            __old_dfs__ = list(handler.__defaults__)
        __annotations__: dict = handler.__annotations__
        __defaults__ = []

        for k, v in __annotations__.items():

            if method!="form":
                if not "{" + k + "}" in self.path and check_is_need_pydantic(v):
                    handler.__annotations__[k] = __wrap_pydantic__(handler.__name__, v)
                    if k != "return":
                        __defaults__ += [fastapi.Body(title=k)]
                    else:
                        self.return_type = handler.__annotations__[k]
            else:
                if k=="return":
                    if check_is_need_pydantic(v):
                        handler.__annotations__[k]=__wrap_pydantic__("",v)

                if not "{" + k + "}" in self.path:
                    import typing
                    if v==fastapi.UploadFile or \
                            (hasattr(v,"__origin__") and v.__origin__==typing.List[fastapi.UploadFile].__origin__
                             and hasattr(v,"__args__") and v.__args__[0]==fastapi.UploadFile):
                        continue
                    elif k!="return" and not v in [str,datetime,bool,float,int]:
                        raise Exception(f"Form post value must be in [str,datetime,bool,float,int")
                    elif k!="return":
                        __defaults__+=[fastapi.Form()]
                        #__wrap_pydantic__(handler.__name__, v)

        __defaults__ += __old_dfs__
        # def new_handler(*args,**kwargs):
        #     handler(*args,**kwargs)
        handler.__defaults__ = tuple(__defaults__)
        self.handler = handler
        if method=="form": method="post"
        self.method = method


def __wrapper_class__(method: str, obj, path: str):
    pass


def __wrapper_func__(method: str, obj, path) -> __hanlder__:
    fx = __hanlder__(method, path, obj)
    return fx


def web_handler(path: str, method: str):
    def warpper(obj):
        import inspect
        if inspect.isclass(obj):
            return __wrapper_class__(method, obj, path)
        elif callable(obj):
            # fx= fastapi.FastAPI()
            # fx.get(response_model=)

            return __wrapper_func__(method, obj, path)

    return warpper
