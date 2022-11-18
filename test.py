from cy_xdoc.models.files import FsFile
from cy_xdoc.services.file_system_object import FileSystemService as F2
class BaseFileService:
    def msg(self, a, b: int) -> FsFile:
        pass

    def check_user(self, usernamer, password) -> bool: pass
    def get_file_by_path(self,file_path:str)->F2:pass


class FileSystemService(BaseFileService):
    @classmethod
    def create(cls, app_name: str, rel_file_path: str, chunk_size: int, size: int):
        pass

    @classmethod
    def test(cls):
        pass


from cy_xdoc.models.files import FsFile


class m_file:

    def create(cls, app_name: str, rel_file_path: str, chunk_size: int, size: int):
        raise NotImplemented

    def test(self):
        raise NotImplemented

    def check_user(self, usernamer, password) -> bool:
        raise NotImplemented

    def msg(self, a, b: int) -> FsFile:
        raise NotImplemented


from typing import TypeVar

T = TypeVar("T")

__provider_cache__ = {}


import cy_kit


fx = cy_kit.provider(FileSystemService, m_file)
fy  = cy_kit.provider(FileSystemService, m_file)
print(fx==fy)