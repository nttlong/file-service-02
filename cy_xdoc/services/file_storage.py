import bson

class FileStorageObject:
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
#         fs_chunks = self.db.get_collection("fs.chunks")
#         fs_chunks.insert_one({
#             "_id": bson.objectid.ObjectId(),
#             "files_id": self.Id,
#             "n": index,
#             "data": content
#         })
#         del content


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

    def get_file_by_name(self, app_name:str, rel_file_path: str)->FileStorageObject:
        """
        Get file by relative path
        :param app_name:
        :param rel_file_path:
        :return:
        """
        pass

    @classmethod
    def get_file_by_id(cls, app_name:str, id:str)->FileStorageObject:
        pass







