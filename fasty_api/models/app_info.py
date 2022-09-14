import datetime
from .error import Error
from typing import Union
from pydantic import BaseModel, Field

class AppInfo(BaseModel):
    """
    Thông tim cơ bản của Application
    """
    AppId: Union[str,None] = Field(description="Application Id cái này đi kèm với secret key sẽ lấy được token")
    """
    Id cua application
    """
    Name:  Union[str,None] =Field(description=f"Tên của app là duy nhất.\n<br/>"
                                f"Một khi đã tạo thì không có cơ hội để điều chỉnh",
                    max_length=50,min_length=5)
    """
    Tên của App không thể điều chỉnh
    """

    LoginUrl: Union[str,None]
    Domain: Union[str,None]
    ReturnUrlAfterSignIn: Union[str,None]
    Description:  Union[str,None]
    CreatedOn: Union[datetime.datetime,None]
    Username:Union[str,None] =Field(description=f"Username for sys admin account of this application")
    Password: Union[str, None] = Field(description=f"Password for sys admin account of of this application")
    Email: Union[str, None]= Field(description=f"Email for sys admin account of of this application")

class EditAppResutl(BaseModel):
    """
    -----------------------------------------------------------------------------------------
    Mô tà kết quả trả về sau khi cập nhật
    -----------------------------------------------------------------------------------------
    """
    Data :Union[AppInfo,None]
    Error: Union[Error,None]
