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
    def close(self):
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

    def copy(self,app_name:str, rel_file_path_from:str , rel_file_path_to, run_in_thread:bool=True)-> FileStorageObject:
        """
        Copy file
        :param rel_file_path_to:
        :param rel_file_path_from:
        :param app_name:
        :param run_in_thread:True copy process will run in thread
        :return:
        """
        pass

    def copy_by_id(self, app_name:str, file_id_to_copy:str,rel_file_path_to:str, run_in_thread:bool)-> FileStorageObject:
        """
        Copy file from id file and return new copy if successful
        :param rel_file_path_to:
        :param app_name:
        :param file_id_to_copy:
        :param run_in_thread:
        :return:
        """
        pass
    