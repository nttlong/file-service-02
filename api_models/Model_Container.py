import ReCompact.dbm
import datetime


@ReCompact.dbm.table(
    "DocContainer",
    keys=["UploadId"],
    index=["OriginalFileName","CreatedOn"]

)
class ZipContainer:
    import bson
    _id = bson.ObjectId,is_require=False)
    UploadId =str,is_require=True) # Trỏ đến UploadRegister
    OriginalFileName =str,is_require=True) # Tên file zip nguyên gốc lúc upload
    Files = list) # Danh sách file zip, chỉ lư địa chỉ tương đối
    CreatedOn =datetime.datetime,is_require=True) #ngày tạo

