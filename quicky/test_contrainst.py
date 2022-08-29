import quicky.object_constraints
@quicky.object_constraints.constraints()
class FileUplaodInfo:
    FileName=(str,True)
    FileSize=(int,True)



data = FileUplaodInfo({
    FileUplaodInfo.FileName : "123",
    FileUplaodInfo.FileSize : 123
})
err=data.get_error()
if err:
    print(err.to_dict())
else:
    print(data.FileSize)
    data.FileSize=123456
    print("OK")
    data.to_dict()