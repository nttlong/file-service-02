import os.path
import pathlib
import sys
from typing import TypeVar

__working_dir__ = pathlib.Path(__file__).parent.__str__()

import cy_kit.cy_kit_x

sys.path.append(__working_dir__)

import cy_kit_x

container = getattr(cy_kit_x, "container")

T = TypeVar('T')


def single(cls: T) -> T:
    return cy_kit_x.single(cls)


def instance(cls: T) -> T:
    return cy_kit_x.instance(cls)


def config_provider(from_class: type, implement_class: type):
    cy_kit.cy_kit_x.config_provider(from_class, implement_class)

from typing import Generic

class Provider(Generic[T]):
    def __init__(self,cls:type):
        self.cls=cls
    @property
    def instance(self)->T:
        return cy_kit_x.provider(self.cls)




def provider(cls: T) -> Provider[T]:
    return Provider[T](cls)


def check_implement(from_class: type, implement_class: T) -> T:
    cy_kit.cy_kit_x.check_implement(from_class, implement_class)
    return implement_class


def must_imlement(interface_class: type):
    return cy_kit.cy_kit_x.must_implement(interface_class)


def yaml_config(path: str, apply_sys_args: bool = True):
    return getattr(cy_kit_x, "yaml_config")(path, apply_sys_args)


def combine_agruments(data):
    return getattr(cy_kit_x, "combine_agruments")(data)
