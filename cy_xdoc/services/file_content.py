import uuid

import cy_docs
from cy_xdoc.services.base import Base
from cy_xdoc.models.files import DocUploadRegister,FsFile,FsChunks
from gridfs import GridIn
import bson
class FileContent:
    def __init__(self,id,db):
        self.id=id
        self.db=db
    @property
    def Id(self):
        return self.id

    def push(self, content:bytes, index:int):

        fs_chunks = self.db.get_collection("fs.chunks")
        fs_chunks.insert_one({
            "_id": bson.objectid.ObjectId(),
            "files_id": self.Id,
            "n": index,
            "data": content
        })
        del content


class FileContentService(Base):

    def create(self, app_name:str, rel_file_path:str, chunk_size:int, size:int)->FileContent:
        mfs = cy_docs.create_file(
            client=self.client,
            db_name=self.db_name(app_name),
            file_name=rel_file_path,
            chunk_size=chunk_size,
            file_size=size
        )
        return FileContent(mfs._id,db=self.client.get_database(self.db_name(app_name)))


    def get_file_by_name(self, app_name, rel_file_path:str):
        upload_id = rel_file_path.split('/')[0].split('.')[0]
        upload = self.db(app_name).doc(DocUploadRegister) @ upload_id
        if upload.MainFileId:
            return FileContent(id =bson.ObjectId(upload.MainFileId),db=self.client.get_database(self.db_name(app_name)))
        return None


