import ReCompact.dbm
import datetime


@ReCompact.dbm.table(
    "DocContainer",
    keys=["UploadId"],
    index=["OriginalFileName","CreatedOn"]

)
class ZipContainer:
    import bson
    _id = ReCompact.dbm.field(data_type=bson.ObjectId,is_require=False)
    UploadId =ReCompact.dbm.field(data_type=str,is_require=True) # Trỏ đến UploadRegister
    OriginalFileName =ReCompact.dbm.field(data_type=str,is_require=True) # Tên file zip nguyên gốc lúc upload
    Files = ReCompact.dbm.field(data_type=list) # Danh sách file zip, chỉ lư địa chỉ tương đối
    CreatedOn =ReCompact.dbm.field(data_type=datetime.datetime,is_require=True) #ngày tạo

