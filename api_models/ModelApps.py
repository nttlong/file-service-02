import ReCompact.dbm
import datetime
@ReCompact.dbm.table(
    "sys_applications",
    keys=["Name","NameLower","Email"],
    index=["Domain","LoginUrl","ReturnUrlAfterSignIn"]

)
class sys_applications:
    import bson
    _id = str)
    Name = str, is_require=True)
    NameLower = str, is_require=True)
    """
    Để cho truy cập nhanh dùng NameLower so sánh với giá trị lower
    """
    RegisteredBy = str,is_require=True)
    RegisteredOn = datetime.datetime, is_require=True)
    ModifiedOn = datetime.datetime, is_require=True)
    Domain = str, is_require=True)
    LoginUrl = str, is_require=True)

    SecretKey = str)
    ReturnUrlAfterSignIn = str,is_require=True)
    Description = str)
    Email= str)
    """
    Email dùng để liên lạc với application khi cần. Ví dụ dùng trong trường ho75ptruy tìm lại mật khẩu của user root trên app
    """


