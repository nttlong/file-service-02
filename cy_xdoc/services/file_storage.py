import typing

import bson


class FileStorageObject:
    @classmethod
    def get_size(cls) -> int:
        pass

    @classmethod
    def seek(cls, position:int):
        pass

    @classmethod
    def tell(cls)->int:
        pass

    @classmethod
    def read(cls, size:int=None)->bytes:
        pass

    @classmethod
    def push(cls,content:bytes, chun_index:int):
        pass

    @classmethod
    def get_id(cls)->str:
        pass




# class FileStorageObject:
#     def __init__(self, id, db):
#         self.id = id
#         self.db = db
#
#     @property
#     def Id(self):
#         return self.id
#
#     def push(self, content: bytes, index: int):



class FileStorageService:
    @classmethod
    def create(cls, app_name: str, rel_file_path: str, chunk_size: int, size: int) -> FileStorageObject:
        """
        Create new file
        :param app_name:
        :param rel_file_path:
        :param chunk_size:
        :param size:
        :return:
        """
        pass

    def get_file_by_name(self, app_name: str, rel_file_path: str) -> FileStorageObject:
        """
        Get file by relative path
        :param app_name:
        :param rel_file_path:
        :return:
        """
        pass

    @classmethod
    def get_file_by_id(cls, app_name: str, id: str) -> FileStorageObject:
        pass

    @classmethod
    def create(cls, app_name: str, rel_file_path: str, chunk_size: int, size: int):
        pass

    @classmethod
    def delete_files(cls, app_name:str, files:typing.List[str], run_in_thread:bool):
        pass

    @classmethod
    def delete_files_by_id(cls, app_name:str, ids:typing.List[str], run_in_thread:bool):
        pass