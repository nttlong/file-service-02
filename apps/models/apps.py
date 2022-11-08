import cy_docs
import datetime
@cy_docs.define(
    name= "sys_applications",
    uniques = ["Name","NameLower","Email"],
    indexes =["Domain","LoginUrl","ReturnUrlAfterSignIn"])
class App:
    _id = str
    Name = str
    NameLower = str
    """
    Để cho truy cập nhanh dùng NameLower so sánh với giá trị lower
    """
    RegisteredBy = str
    RegisteredOn = datetime.datetime
    ModifiedOn = datetime.datetime
    Domain = str
    LoginUrl = str

    SecretKey = str
    ReturnUrlAfterSignIn = str
    Description = str
    Email = str
    """
    Email dùng để liên lạc với application khi cần. Ví dụ dùng trong trường ho75ptruy tìm lại mật khẩu của user root trên app
    """