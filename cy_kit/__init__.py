import os.path
import pathlib
import sys
from typing import TypeVar

if sys.platform == "linux":
    sys.path.append(
        os.path.join(
            pathlib.Path(__file__).parent.__str__(),
            "build", "lib.linux-x86_64-3.8", "cy_kit"
        )
    )
else:
    raise Exception(f"not support for {sys.platform}")
import cy_kit_x

container = getattr(cy_kit_x, "container")

T = TypeVar('T')


def single(cls: T) -> T:
    return getattr(cy_kit_x, "single")(cls)
def instance(cls: T) -> T:
    return getattr(cy_kit_x, "instance")(cls)
def yaml_config(path:str):
    return getattr(cy_kit_x, "yaml_config")(path)
def combine_agruments(data):
    return getattr(cy_kit_x,"combine_agruments")(data)