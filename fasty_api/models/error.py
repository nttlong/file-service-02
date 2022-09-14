import datetime
from typing import List, AnyStr, Union
from ReCompact.db_async import Error,ErrorType
from pydantic import BaseModel, Field
ErrorType=ErrorType

class Error(BaseModel):
    """
    Thông tin chi tiết của lỗi
    """
    Code:Union[str,None] = Field( description="Mã lỗi:<ol>\n"
                                   "<li>DuplicateData: Trùng thông tin</li>\n"
                                   "<li>DataWasNotFound: Không tìm thấy dữ liệu</li>\n"
                                              "<li>MissingField: Thiếu thông tin"
                                   "<li>System: Lỗi hệ thống</li>\n"
                                   "</ol>")
    Message: Union[str,None]
    Fields:Union[List[str],None]=Field(description="Danh sách các thông tin gây ra lỗi")
