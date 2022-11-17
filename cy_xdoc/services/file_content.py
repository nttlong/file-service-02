import uuid

from cy_xdoc.services.base import Base


class FileContent:
    def __init__(self):
        self._id_ = str(uuid.uuid4())
    @property
    def Id(self):
        return self._id_

    def push(self, content:bytes, index:int):
        pass


class FileContentService(Base):



    def create(self, app_name:str, rel_file_path:str, chunk_size:int, size:int)->FileContent:
        pass
