class BaseFileService:
    @classmethod
    def ok(cls):
        pass





class FileSystemService(BaseFileService):
    @classmethod
    def create(cls, app_name: str, rel_file_path: str, chunk_size: int, size: int):
        pass

    @classmethod
    def test(cls):
        pass
from  typing import TypeVar
T=TypeVar("T")


def provider(interface:type,implement:T)->T:
    import inspect
    interface_methods= {}
    for x in interface.__bases__:
        for k,v in x.__dict__.items():
            if k[0:2]!="__" and k[:-2]!="__" and not inspect.isclass(v) and callable(v):
                interface_methods[k]=v
    for k, v in interface.__dict__.items():
        if k[0:2] != "__" and k[:-2] != "__" and not inspect.isclass(v) and callable(v):
            interface_methods[k] = v
    implement_methods={}

    for k, v in implement.__dict__.items():
        if k[0:2] != "__" and k[:-2] != "__" and not inspect.isclass(v) and callable(v):
            implement_methods[k] = v
    interface_method_name_set = set(interface_methods.keys())
    implement_methods_name_set = set(implement_methods.keys())
    miss_name = interface_method_name_set.difference(implement_methods_name_set)
    if miss_name.__len__()>0:
        msg =""
        for x in miss_name:
            msg+=f"{x} is missing in {implement.__module__}.{implement.__name__}\n"
        raise Exception(msg)




