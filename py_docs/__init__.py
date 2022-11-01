import os.path
import pathlib
import ctypes
import sys

__working_dir__ = pathlib.Path(__file__).parent.__str__()
if sys.platform != "linux":
    raise Exception(f"The module is not available for {sys.platform}")
__cy_docs_path__ = os.path.join(
    __working_dir__,
    "build", "lib.linux-x86_64-3.8", "py_docs"
)
sys.path.append(__cy_docs_path__)
import cy_docs
from typing import TypeVar, Generic, List

T = TypeVar('T')


def expr(cls: T) -> T:
    """
    Create mongodb build expression base on cls
    :param cls:
    :return:
    """
    return cy_docs.fields
