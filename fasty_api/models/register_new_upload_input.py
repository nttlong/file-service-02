from typing import List, Union, Optional
from pydantic import Field, BaseModel
from . import error
class RegisterUploadInfo(BaseModel):
    """
    Bảng ghi thông tin đăng ký upload
    """
    FileName:Union[str,None]=Field(description="Tên file upload")
    ChunkSizeInKB:Union[int,None]=Field(description="Kích thước phân đoạn tính bằng KB")
    FileSize:Union[int,None]=Field(description="Kích thước file tính bằng bytes")
    IsPublic:Optional[bool]=Field(description="Phạm vi truy cập\n <ol>"
                                                "<li>True:  không ngăn cản bởi xác thực</li>\n"
                                                "<li>False: Buộc phải chứng thực\n</li></ol>",
                                  default=False)
    ThumbConstraints:Optional[str]=Field(
        description="Thumbnail constraint generator: After material successfully uploaded. The system will generate a default thumbnail in size of 700pxx700px. However if thy desire more thumbnails with various  sizes such as: 200x200,450x450,... Thy just set 200,450,.. Example: for 200x200, 350x350 and 1920x1920 just set 200,350,1920",
        default=""
    )

class RegisterUploadResult(BaseModel):
    NumOfChunks:Union[int,None]=Field(description="Số phân đoạn")
    """
    Số phân đoạn: Rất quan trọng dùng để hỗ trợ client upload 
    """
    ChunkSizeInBytes: Union[int,None] = Field(description="Kích thước phân đoạn tính bằng byte")
    """
    Kích thước phân đoạn: Rất quan trọng dùng để hỗ trợ client upload
    """
    UploadId: Union[str,None] = Field(description="Upload ID")
    """
    Upload Id: Hỗ trơ các ứng dụng khác lấy thông tin
    """
    ServerFilePath: Union[str,None] = Field(description=f"Đường dẫn đến file tại server\n<br>"
                                                        f"Để xem nội dung file <host-url>/<api-sub-dir>/file/<ServerFilePath><br>\n"
                                                        f"Thông thường thì <api-sub-dir> là api, nhưng cũng có thể là gốc")
    """
    Đường dẫn đến file tại server: Rất quan trọng các ứng dụng khác sẽ lưu lại thông tin này
    """
    MimeType:Union[str,None] =Field(description="Mime Type")
    """
    Mime type:: Rất quan trọng các ứng dụng khác sẽ lưu lại thông tin này
    """
    RelUrlOfServerPath:Union[str,None] =Field(description="Đường dẫn tương đối để xem hoặc tãi nội dung (không có url gốc)")
    """
    Đường dẫn tương đối để xem hoặc tãi nội dung (không có url gốc)\n
    Rất quan trọng các ứng dụng khác sẽ lưu lại thông tin này
    """
    SizeInHumanReadable:Union[str,None] =Field(description="Dung lương ghi ra dạng text")
    UrlOfServerPath:Union[str,None] =Field(description="Url đầy đủ để xem hoặc tải nội dung file")
    OriginalFileName: Union[str,None] = Field(description="Tên file gốc lúc upload")
    """
    Tên file gốc lúc upload
    """
    UrlThumb: Union[str,None]=Field(description="Đường dẫn đầy đủ đến ảnh Thumb")
    """
    Đường dẫn đầy đủ đến ảnh Thumb
    """
    RelUrlThumb: Union[str, None] = Field(description="Đường tương đối đến ảnh Thumb\n<br><host api url>+RelUrlThumb=UrlThumb")
    """
    Đường tương đối đầy đủ đến ảnh Thumb
    """
    FileSize:Union[int,None] = Field(description="Kích thước file")


class RegisterUploadInfoResult(BaseModel):
    """
    Bảng ghi cấu trúc trả vể cho API upload
    """
    Data:Union[RegisterUploadResult,None]=Field(description="Thông tin dăng ký")
    Error:Union[error.Error,None] = Field(description="nếu không thành công lỗi ở đây")