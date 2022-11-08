import dbm

import ReCompact.dbm


@dbm.table(
    "Sys_Users",
    keys =["UserName","Email","Salary,Code"],
    index=["a","a,b"]
)
class User:
    import bson
    _id = bson.objectid)
    UserName=dbm.field(is_require=True)
    Email = dbm.field(is_require=True)

@dbm.table(
    table_name ="UploadRegister",
    keys=["ServerFileName"]

)
class UploadRegister:
    import pymongo
    import  bson
    _id= bson.objectid)
    ServerFileName = str,max_len=50,is_require=True)
