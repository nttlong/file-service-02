import cy_docs
class Users:
    first_name:str
    LastName:str


class MyInfo:
    MyCode:str
    User:Users

fx=cy_docs.cy_docs_x.Field(MyInfo)
v=fx.user
print(v)