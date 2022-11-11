import os.path
import pathlib
import pymongo.mongo_client
import ctypes
import sys
__release_mode__ = True
__working_dir__ = pathlib.Path(__file__).parent.__str__()
if sys.platform != "linux":
    raise Exception(f"The module is not available for {sys.platform}")

__cy_docs_path__ = os.path.join(
    __working_dir__,
    "build", "lib.linux-x86_64-3.8", "cy_docs"
)
root_dir,dirs,_ = list(os.walk(os.path.join(__working_dir__,"build")))[0]
for x in dirs:
    sys.path.append(os.path.join(root_dir,x,"cy_docs"))

sys.path.append(__cy_docs_path__)
if not __release_mode__:
    from . import cy_docs_x
else:
    import cy_docs_x
from typing import TypeVar, Generic, List

T = TypeVar('T')


def expr(cls: T) -> T:
    """
    Create mongodb build expression base on cls
    :param cls:
    :return:
    """
    return getattr(cy_docs_x,"fields")
def get_doc(collection_name: str, client: pymongo.mongo_client.MongoClient, indexes: List[str] = [],
            unique_keys: List[str] = []):

    return getattr(cy_docs_x,"Document")(collection_name, client,indexes=indexes,unique_keys=unique_keys)
def define(name:str,indexes:List[str],uniques:List[str]):
    return getattr(cy_docs_x,"document_define")(name,indexes,uniques)