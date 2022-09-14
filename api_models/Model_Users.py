import ReCompact.dbm
import datetime
import bson
from .ModelApps import sys_applications
field= ReCompact.dbm.field
@ReCompact.dbm.table(
    "sys_users",
    keys=["Username","Email","UsernameLowerCase","HashPassword"]

)
class User:
    _id = field(data_type=bson.ObjectId)
    Username = field(data_type=str,is_require= True)
    UsernameLowerCase = field(data_type=str,is_require=True)
    Password =field(data_type=str,is_require= True)
    HashPassword =field(data_type=str,is_require= True)
    PasswordSalt =field(data_type=str,is_require= True)
    Email = field(data_type=str,is_require= True)
    LoginCount =field(data_type=int,is_require=True)
    """
    Số lần login
    """
    LastestPasswordChangeOn = field(data_type=datetime.datetime)
    """
    Lần cuối sửa mật khẩu
    """
    Application:sys_applications= field(data_type=sys_applications,is_require=True)
    CreatedOn= field(data_type=datetime.datetime,is_require= True)
    IsLocked= field(data_type=bool,is_require=True)
    LockedOn = field(data_type=datetime.datetime)

