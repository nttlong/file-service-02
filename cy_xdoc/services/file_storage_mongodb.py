import uuid

import cy_docs
import cy_kit
from cy_xdoc.services.base import Base
from cy_xdoc.models.files import DocUploadRegister,FsFile,FsChunks
from gridfs import GridIn
import bson

from cy_xdoc.services.file_storage import FileStorageService,FileStorageObject
@cy_kit.must_imlement(FileStorageObject)
class MongoDbFileStorage:
    pass
@cy_kit.must_imlement(FileStorageService)
class MongoDbFileService(Base):
    def create(cls, app_name: str, rel_file_path: str, chunk_size: int, size: int) -> MongoDbFileStorage:
        raise NotImplemented

    def get_file_by_name(self, app_name, rel_file_path: str) -> MongoDbFileStorage:
        raise NotImplemented

    # def create(self, app_name:str, rel_file_path:str, chunk_size:int, size:int)->FileStorage:
    #     mfs = cy_docs.create_file(
    #         client=self.client,
    #         db_name=self.db_name(app_name),
    #         file_name=rel_file_path,
    #         chunk_size=chunk_size,
    #         file_size=size
    #     )
    #     return FileStorage(mfs._id, db=self.client.get_database(self.db_name(app_name)))
    #
    #
    # def get_file_by_name(self, app_name, rel_file_path:str):
    #     upload_id = rel_file_path.split('/')[0].split('.')[0]
    #     upload = self.db(app_name).doc(DocUploadRegister) @ upload_id
    #     if upload.MainFileId:
    #         return FileStorage(id =bson.ObjectId(upload.MainFileId), db=self.client.get_database(self.db_name(app_name)))
    #     return None


