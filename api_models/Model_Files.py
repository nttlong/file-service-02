import ReCompact.dbm
import datetime
import bson
field= ReCompact.dbm.field
@ReCompact.dbm.table(
    "DocUploadRegister",
    keys=["ServerFileName", "FullFileName","FullFileNameLower"],
    index=[
        "RegisteredOn",
        "RegisteredOnDays",
        "RegisteredOnMonths",
        "RegisteredOnYears",
        "RegisteredOnHours",
        "RegisteredOnMinutes",
        "RegisteredOnSeconds",
        "Status",
        "FileExt",
        "FileName",
        "MainFileId",
        "ThumbFileId",
        "OriginalFileId",
        "ProcessHistories.ProcessOn",
        "ProcessHistories.ProcessAction",
        "ProcessHistories.UploadId",
        "OCRFileId",
        "FileNameLower",
        "FullFileNameLower",
        "PdfFileId",
        "FullFileNameWithoutExtenstion",
        "FullFileNameWithoutExtenstionLower"

    ]

)

class DocUploadRegister:
    """
    Cấu trúc của thông tin Upload.

    """
    @ReCompact.dbm.table(
        "DocUploadRegister_Processhistory",
        keys= ["ProcessOn,UploadId"]
    )
    class ProcessHistory:
        """
        Thông tin lịch sử của các tiến trình xử lý sẽ được ghi nhận theo cấu trúc bản ghi này
        """
        _id = field(bson.ObjectId)
        ProcessOn = field(datetime.datetime,is_require=True)
        """
        Thời điểm đã hoàn tất xử lý
        """
        ProcessAction = field(str,is_require= True)
        """
        Loại xử lý nào đã được hòa tất.\n
        Ví dụ:
            Ảnh Thumnb của Office File giá trị này sẽ là "files.services.thumnb.office
        """
        UploadId = field(str,is_require= True)
        """
        Ghi nhận lại Id của File đã xử lý
        """


    _id = field(str)
    FileNameOnly = field(str, is_require=True)
    """
    Tên file không có phần Extent đã được lowercase\n
    Để bảo đảm tốc độ hệ thống ghi nhận luôn thông tin này khi upload mà không cần tính lại\n
    
    
    """
    FileName = field(str, is_require=True)
    """
    Tên file gốc, là tên file lúc người dùng hoặc 1 ứng dụng nào đó Upload
    """
    FileNameLower = field(str, is_require=True)
    """
    Tên file gốc dạng lowe case để bảo đảm tốc độ truy cập
    """
    RegisterOn = field(datetime.datetime, is_require=True)
    """
    Thời điểm bắt đầu Upload.
    Lưu ý: Việc Upload 1 File có thể kéo dài trong vài phút
    """
    RegisterOnDays =field(int, is_require=False)
    """
    Ngày tạo\n
    Ví dụ RegisterOn là 22/8/1732 thì RegisterOnDays là 22 \n
    Để bảo đảm tốc độ khi cần truy vấn thông tin hệ thống sẽ tính luôn ngày của ngày tạo
     
    """
    RegisterOnMonths = field(int, is_require=False)
    """
        Tháng của agày tạo\n
        Ví dụ RegisterOn là 22/8/1732 thì RegisterOnMonths là 8 \n
        Để bảo đảm tốc độ khi cần truy vấn thông tin hệ thống sẽ tính luôn ngày của ngày tạo

        """
    RegisterOnYears = field(int, is_require=False)
    RegisterOnHours = field(int, is_require=False)
    RegisterOnMinutes = field(int, is_require=False)
    RegisterOnSeconds = field(int, is_require=False)

    LastModifiedOn = field(datetime.datetime, is_require=False)
    """
    Thời điểm thông tin bị điều chỉnh
    """
    Status = field(int, is_require=True)
    """
    Tình trạng của File: 0- Chưa xong, cần phải Resume Upload hoặc có thể xóa bò
                         1- Nội dung chính đã hoàn chỉnh
    """
    SizeInBytes = field(int, is_require=True)
    """
    Độ lớn của file tính bằng Bytes \n
    Lưu ý trong Python 3 kiểu int có thể lưu lại 1 con số lớn
    Vì vậy kích thước file có thể lưu được là  858,993,459,2 GB
    """
    ChunkSizeInKB = field(int, is_require=True)
    """
    Việc Upload 1 file lớn chỉ trong 1 lần là điều không thể:
        Quá trình Upload sẽ cắt file thành những đoạn nhỏ rồi Upload. \n
        Các đoạn nhỏ này sẽ ghép lại thành 1 file duy nhất trên server. \n
        Nhưng hệ thống này đang dùng MongoDb để lưu trữ. Các đoạn nhỏ này vẫn được giữ nguyên
        và có thể bị phân tán ở những Node khác nhau của MongoDB.\n
        Thông tin này ghi nhận kích thước của một đoạn nhỏ tính bằng KB
         
        
    """
    ChunkSizeInBytes = field(int, is_require=True)
    NumOfChunks = field(int, is_require=True)
    FileExt = field(str, is_require=False)
    SizeInHumanReadable = field(str, is_require=False)
    PercentageOfUploaded = field(float, is_require=False)
    ServerFileName = field(str, is_require=False)
    RegisteredBy = field(str, is_require=False)
    IsPublic = field(bool, is_require=True)
    """
    Một số nội dung Upload có thể cần phải công khai \n
    Trường hợp này đặt IsPublic là True 
    """
    FullFileName = field(str, is_require=True)
    """
    Là đường dẫn đầy đủ của File sau khi lưu hoàn tất trên server.
    Đường dẫn đầy đủ tính như sau:
    Sau khi file Upload xong Mongodb sẽ phát sinh 1 id trong trong bảng ghi này \n
    Lấy Id +'/'+<tên file gốc> ra đường dẫn đầy đủ
    Với trường hợp Upload 1 File ZIP và thực hiện tiến trình giải nén ngay tại server.\n
    Thì đường dẫn của file nằm bê trong cộng với tiền tố là Id sẽ cho ra đường dẫn đầy đủ:
    Ví dụ:\n
        Trong File ZIP có file mydoc.txt nằm trong thư mục documents/2001.\n
        Và UploadId là 111-1111-111-1111 \n
        Thì đường dẫn đầy đủ là 111-1111-111-1111/documents/2001/mydoc.txt \n
    Các ứng dụng khác khi cần duy trì đầy đủ cấu trúc của thư mục và file có thể cập nhật lại đường dẫn này \n
    Theo quy tắc <UploadId>/<Đường dẫn tương đối tính từ gốc>
    
    
    
    """
    FullFileNameLower = field(str, is_require=True)
    """
    Đường dẫn dạng lower , tắng tốc khi truy cập
    """

    FullFileNameWithoutExtenstion = field(str, is_require=True)
    """
    Là FullFileName nhưng lược bỏ phần mở rộng\n
    Tại sao lại có điều này?
    Mỗi một file được upload lên server sẽ có thể phát sinh các file sau:
    1-File OCR: nếu file upload lên dạng pdf ảnh hoặc dạng image chưa có lớp text nhạn dạng hệ thống sẽ 
                triệu hồi 1 trong 2 dịch vụ nằm trong consumers/file_service_upload_ocr_pdf nếu là file pdf
                hoặc consumer/files_service_upload_orc_image.py nếu là file image.
    2- File thumb: ảnh thu gọn đại diện của file.
    3- Pdf: là file pdf phát sinh từ file office
    
    Tất cả các url truy cập đến nội dung OCR, Thumb, Pdf,... đều dùng FullFileName làm chuẩn
    Sau đó chỉ việc thay đổi phần mở rộng và phần tiền tố
    Ví dụ file gốc là test.docx
    FullFileName server là 123-323-189fd/test.docx
    Khi đó url vào file gốc là <Host-api>/<app-__name__>/file/123-323-189fd/test.docx
    Khi đó url vào file thumb là <Host-api>/<app-__name__>/thumb/123-323-189fd/test.png
    Khi đó url vào file orc là <Host-api>/<app-__name__>/file-ocr/123-323-189fd/test.pdf
    Khi đó url vào file pdf là <Host-api>/<app-__name__>/file-pdf/123-323-189fd/test.pdf
    Vì vậy các API tiếp nhận request sẽ lấy phần 123-323-189fd/test để truy tìm file fs 
    trong Mongodb để write xuống thiết bị yêu cầu đúng nôi dung mà nó đang chứa đưng
    Để truy tìm file FS trong MongoDb một cách nhanh chóng hệ thống sẽ dự vào FullFileNameWithoutExtenstion
    dạng lower case đểm tìm
    
    """
    FullFileNameWithoutExtenstionLower =field(str, is_require=True)
    """
    Là FullFileNameWithoutExtenstion  dạng lower case
    """
    ThumbWidth = field(int, is_require=False)
    """
    Độ rộng của ảnh Thumb tính bằng Pixel \n
    Thông tin này chỉ có khi tiến trình tạo ảnh Thumb hoàn tất.
    Hầu hết các nôi dung Upload có ảnh Thumb. Một số trường hợp không có ảnh Thumb giá trị này sẽ là null
    """
    ThumbHeight = field(int, is_require=False)
    """
        Độ rộng của ảnh Thumb tính bằng Pixel \n
        Thông tin này chỉ có khi tiến trình tạo ảnh Thumb hoàn tất.
        Hầu hết các nôi dung Upload có ảnh Thumb. Một số trường hợp không có ảnh Thumb giá trị này sẽ là null
    """
    MimeType = field(str, is_require=False)
    """
    Xem link: https://developer.mozilla.org/en-US/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Common_types
    """
    SizeUploaded =field(int,is_require=False)
    """
    Dung lượng đã upload tính bằng bytes
    """
    NumOfChunksCompleted = field(int, is_require=False)
    """
    Số chunk đã hoàn tất.
    Thông tin này rất quan trọng,
    Nếu sau này có nhu cầu Resume Upload (Tức là upload tiếp các nội dung chưa xong)
    Resume Upload phía Client sẽ dựa vào thông tin này để đọc file và Upload tiếp
    """
    MainFileId = field(bson.ObjectId)
    ThumbFileId =field( bson.ObjectId)
    """
    Id ảnh Thumb của file này.
    Mỗi một file trên server nếu có ảnh Thumb, ảnh thumb sẽ lưu trong GridFS với một Id.
    Giá trị của Id trong GridFS được gán vào ThumbFileId
    """
    ThumbId  = field(str) # depreciate after jun 2022
    HasThumb = field(bool)
    """
    Thông tin này có được sau khi tiến trình phân tích và xác định ảnh thumb chạy xong.
    
    """
    OriginalFileId = field(bson.ObjectId)
    """
    Trường hợp xử lý OCR thành công \n
    Thông tin này sẽ lưu lại file gốc, trong khi đó file gốc sẽ được cập nhật lại bằng nôi dung file mới
    đã được OCR
    """

    OCRFileId = field(bson.ObjectId)
    VideoDuration = field(int)
    """
    Thời lượng tính bằng giây
    """
    VideoFPS = field(int)
    """
    Số khung hình trên giây, thông tin này rất quan trọng trong việc tối ưu streaming nội dung video
    """
    VideoResolutionWidth = field(int)
    """
    Độ phân giài ngang: \n
    Đây là thông tin cực kỳ quan trọng trong quá trìn streaming \n
    ví dụ: độ phân giải 4096x2160 pixels lấy 4096/1024=4 => Chất lượng 4K
    Để giúp server streaming tốt video chất lượng 4K thì phải đặt streaming buffering là
    4*1024*3= 4096(pixels) x (1 byte RED+ 1 byte GREEN + 1 byte BLUE)
    Tuy nhiên để tính được chính xác cần phải cân nhắc đến yếu tố Bit Rate
    """
    VideoResolutionHeight = field(int)  # Độ phân giải dọc
    ProcessHistories =  field(list)
    """
    Lịch sử các quá trình xử lý
    """
    PdfFileId=field(bson.ObjectId)
    """
    Field này là file id trỏ đến file pdf, là file pdf sinh ra bằng cách dùng
    libreoffice convert ra pdf 
    """
    MarkDelete = field(bool)
    """
    Mark delete
    """
    AvailableThumbSize = field(str)
    """
    Thumbnail constraint generator: After material successfully uploaded. The system will generate a default thumbnail in size of 700pxx700px. However if thy desire more thumbnails with various  sizes such as: 200x200,450x450,... Thy just set 200,450,.. Example: for 200x200, 350x350 and 1920x1920 just set 200,350,1920
    """
    AvailableThumbs = field(type([]))
    IsProcessed = field(bool)
@ReCompact.dbm.table(
    "fs.files",
    keys=["rel_file_path"],
    index=["filename"]
)
class FsFile:
    _id = field(bson.ObjectId)
    rel_file_path=field(str)
    filename=field(str)
@ReCompact.dbm.table(
    "fs.chunks",
    index=["files_id","n","files_id,n"]
)
class FsChunks:
    _id = field(bson.ObjectId)
    files_id= field(bson.ObjectId)
    n= field(int)
    data =field(bytes)
@ReCompact.dbm.table(
    "MediaTracking",
    index=["UploadId,CurrentChunkIndex","UploadId","CurrentChunkIndex"]
)
class MediaTracking:
    _id = field(bson.ObjectId)
    UploadId =field(str)
    FileXet = field(str)
    NumOfChunks =field(int)
    file_id = field(bson.ObjectId)
    AppName = field(str)
    CreatedOn = field(datetime)
    PlugInRunner = field(dict)
    IsSync = field(bool)
    Status = field(int)
    IsInSync= field(bool)
    StartDownloadAt = field(datetime.datetime)
    IsDownloadComplete = field(bool)
    EndDownloadAt = field(datetime.datetime)
    DownloadTimeInSeconds = field(float)

@ReCompact.dbm.table(
    "Sys_messages",
    index=["MsgType","CreatedOn","AppName","MsgId"]
)
class SysMessage:
    """
    Message
    """
    _id = field(bson.ObjectId)
    MsgId = field(str)
    AppName=field(str)
    MsgType=field(str)
    Data=field(dict)
    CreatedOn = field(datetime)
    IsFinish = field(bool)
    IsLock = field(bool)
    InstancesLock = field(dict)
    RunInsLock = field(str)