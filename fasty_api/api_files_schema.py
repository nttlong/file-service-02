from typing import Union

from pydantic import BaseModel

class Filter(BaseModel):
    """
    Bộ lọc
    """
    PageIndex: int=0
    """
    Bỏ qua
    """
    PageSize: int =50
    FieldSearch: Union[str,None]
    """
    Filed cần tìm
    """
    ValueSearch: Union[str,None]
    class Config:
        schema_extra = {
            "filter": {
                "PageIndex": 0,
                "PageSize":50
            }
        }

class FileInfo(BaseModel):
    FileName: str
