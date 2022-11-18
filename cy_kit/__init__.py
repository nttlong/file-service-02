import os.path
import pathlib
import sys
from typing import TypeVar
__working_dir__ = pathlib.Path(__file__).parent.__str__()
sys.path.append(__working_dir__)

import cy_kit_x
container = getattr(cy_kit_x, "container")

T = TypeVar('T')


def single(cls: T) -> T:
    return cy_kit_x.single(cls)


def instance(cls: T) -> T:
    return cy_kit_x.instance(cls)
def provider(from_class:type,implement_class:T)->T:
    return cy_kit_x.provider(from_class,implement_class)

def yaml_config(path: str, apply_sys_args: bool = True):
    return getattr(cy_kit_x, "yaml_config")(path, apply_sys_args)


def combine_agruments(data):
    return getattr(cy_kit_x, "combine_agruments")(data)
