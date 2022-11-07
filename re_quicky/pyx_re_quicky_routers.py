from datetime import datetime
import inspect
import fastapi
import pydantic
import sys
def __wrap_pydantic__(pre, cls):
    if hasattr(cls, "__annotations__"):
        ls = list(cls.__dict__.items())
        for k, v in ls:
            if not (k[0:2] == "__" and k[:-2] != "__") and v not in [str, int, datetime, bool,
                                                                     float] and inspect.isclass(v):
                re_modify = __wrap_pydantic__(cls.__name__, v)
                cls.__annotations__[k] = re_modify
                setattr(sys.modules[cls.__module__], k, re_modify)

        for k, v in cls.__annotations__.items():
            if v not in [str, int, datetime, bool, float] and inspect.isclass(v):
                if cls.__annotations__.get(k) is None:
                    re_modify = __wrap_pydantic__(cls.__name__, v)
                    cls.__annotations__[k] = re_modify
                    setattr(sys.modules[cls.__module__], k, re_modify)

    ret_cls = type(f"{cls.__name__}", (cls, pydantic.BaseModel,), dict(cls.__dict__))
    setattr(sys.modules[cls.__module__], cls.__name__, ret_cls)
    ret_cls.__name__ = cls.__name__
    return ret_cls
def check_is_need_pydantic(cls:type):
    ret = (cls not in [str, int, float, datetime,bool,dict]) and (inspect.isclass(cls) and (not issubclass(cls,pydantic.BaseModel)))
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

            if not "{"+k+"}" in self.path  and check_is_need_pydantic(v):
                print(f"apply pydantic.BaseModel to {v.__module__}.{v.__name__}")
                handler.__annotations__[k] = __wrap_pydantic__(handler.__name__, v)
                if k !="return":
                    __defaults__ += [fastapi.Body(title=k)]
                else:
                    self.return_type = handler.__annotations__[k]
        __defaults__ += __old_dfs__
        # def new_handler(*args,**kwargs):
        #     handler(*args,**kwargs)
        handler.__defaults__ = tuple(__defaults__)
        self.handler = handler
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




