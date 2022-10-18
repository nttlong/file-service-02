from typing import TypeVar, Generic, List
from enum import Enum
class ErrorCode(Enum):
    NONE ="none"
T = TypeVar('T')
class Error:
    def __init__(self):
        self.code:ErrorCode=None
class ServiceResult(Generic[T]):
    def __init__(self) -> None:
        self.result:T=None
        self.error:Error =None
