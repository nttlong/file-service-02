import datetime

import bson

import ReCompact
import ReCompact.db_async


@ReCompact.document(
    name="Sys_JWT_Users",
    keys=["Email", "Username", "UsernameLowerCase"],
    indexes=["HashPassword"]
)
class User:
    """
    Thông tin user
    Mỗi một database sẽ có 1 collection user
    """
    _id = (bson.ObjectId)
    Username = (str)
    UsernameLowerCase = (str)
    HashPassword = (str)
    Email = (str)
    IsLocked = (bool),
    CreatedOn = (datetime.datetime)
    CreatedOnUTC = (datetime.datetime)
    ModifiedOn = (datetime.datetime)
    IsSysAdmin = (bool)



@ReCompact.document(
    name="SYS_SingleSignOn",
    keys=[ "SSOID"],
    indexes=["Token","Application","Application,Token","Application,SSOID","ReturnUrlAfterSignIn"]

)
class SSO:
    _id = (bson.ObjectId)
    Token = (str)
    SSOID = (str)
    CreatedOn = (datetime.datetime)
    Application = (str)
    ReturnUrlAfterSignIn =(str)



Users = User()
"""
Mongodb document of user
"""
SSOs = SSO()
