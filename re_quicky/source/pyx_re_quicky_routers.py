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
                cls.__annotations__[k] = __wrap_pydantic__(cls.__name__, v)
                setattr(cls, k, None)

        for k, v in cls.__annotations__.items():
            if v not in [str, int, datetime, bool, float] and inspect.isclass(v):
                if cls.__annotations__.get(k) is None:
                    cls.__annotations__[k] = __wrap_pydantic__(cls.__name__, v)
                    setattr(sys.modules[cls.__moduel__], k, None)

    ret_cls = type(f"__dynamic_{pre}_{cls.__name__}__", (cls, pydantic.BaseModel,), dict(cls.__dict__))
    ret_cls.__name__ = f"__dynamic_{pre}_{cls.__name__}__"
    return ret_cls
def check_is_need_pydantic(cls:type):
    ret = (cls not in [str, int, float, datetime,bool]) and (inspect.isclass(cls) and (not issubclass(cls,pydantic.BaseModel)))
    return ret
class __hanlder__:

    def __init__(self, method, path, handler):
        self.path = path
        __old_dfs__ = []
        if handler.__defaults__ is not None:
            __old_dfs__ = list(handler.__defaults__)
        __annotations__: dict = handler.__annotations__
        __defaults__ = []
        for k, v in __annotations__.items():
            print(f"apply pydantic.BaseModel to {v.__module__}.{v.__name__}")
            if check_is_need_pydantic(v):
                print(f"apply pydantic.BaseModel to {v.__module__}.{v.__name__}")
                handler.__annotations__[k] = __wrap_pydantic__(handler.__name__, v)

            __defaults__ += [fastapi.Body(title=k)]
        __defaults__ += __old_dfs__
        # def new_handler(*args,**kwargs):
        #     handler(*args,**kwargs)
        handler.__defaults__ = tuple(__defaults__)
        self.handler = handler
        self.method = method

def __wrapper_class__(method: str, obj, path: str):
    pass


def __wrapper_func__(method: str, obj, path) -> __hanlder__:
    return __hanlder__(method, path, obj)
def web_handler(path: str, method: str):
    def warpper(obj):
        import inspect
        if inspect.isclass(obj):
            return __wrapper_class__(method, obj, path)
        elif callable(obj):
            return __wrapper_func__(method, obj, path)

    return warpper




