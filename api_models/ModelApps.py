import ReCompact.dbm
import datetime
@ReCompact.dbm.table(
    "sys_applications",
    keys=["Name","NameLower","Email"],
    index=["Domain","LoginUrl","ReturnUrlAfterSignIn"]

)
class sys_applications:
    import bson
    _id = ReCompact.dbm.field(data_type=str)
    Name = ReCompact.dbm.field(data_type=str, is_require=True)
    NameLower = ReCompact.dbm.field(data_type=str, is_require=True)
    """
    Ten cua app
    """
    RegisteredBy = ReCompact.dbm.field(data_type=str,is_require=True)
    RegisteredOn = ReCompact.dbm.field(data_type=datetime.datetime, is_require=True)
    ModifiedOn = ReCompact.dbm.field(data_type=datetime.datetime, is_require=True)
    Domain = ReCompact.dbm.field(data_type=str, is_require=True)
    LoginUrl = ReCompact.dbm.field(data_type=str, is_require=True)

    SecretKey = ReCompact.dbm.field(data_type=str)
    ReturnUrlAfterSignIn = ReCompact.dbm.field(data_type=str,is_require=True)
    Description = ReCompact.dbm.field(data_type=str)
    Email= ReCompact.dbm.field(data_type=str)
    """
    Email dùng để liên lạc với application khi cần. Ví dụ dùng trong trường ho75ptruy tìm lại mật khẩu của user root trên app
    """


