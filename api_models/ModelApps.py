import ReCompact.dbm
import datetime
field =ReCompact.dbm.field
@ReCompact.dbm.table(
    "sys_applications",
    keys=["Name","NameLower","Email"],
    index=["Domain","LoginUrl","ReturnUrlAfterSignIn"]

)
class sys_applications:
    import bson
    _id = field( str)
    Name = field( str, is_require=True)
    NameLower = field( str, is_require=True)
    """
    Để cho truy cập nhanh dùng NameLower so sánh với giá trị lower
    """
    RegisteredBy = field( str,is_require=True)
    RegisteredOn = field( datetime.datetime, is_require=True)
    ModifiedOn = field(datetime.datetime, is_require=True)
    Domain = field(str, is_require=True)
    LoginUrl = field(str, is_require=True)

    SecretKey = field(str)
    ReturnUrlAfterSignIn = field( str,is_require=True)
    Description = field( str)
    Email= field(str)
    """
    Email dùng để liên lạc với application khi cần. Ví dụ dùng trong trường ho75ptruy tìm lại mật khẩu của user root trên app
    """


