import datetime
import re

import enigma_docs
from enigma_docs import Document
from typing import List
class Departments:
    def __init__(self):
        self.Number:int = None
        self.CreatedOn:datetime = None
        self.Code:str = None

    pass
class SysUser:
    def __init__(self):
        self.Name = None
        self.departments : List[Departments]=[]
        self.department: Departments =None
        self.Address = None
        self.Phones=[]

    def add_department(self, param:Departments):
        pass


from pymongo.mongo_client import MongoClient
client = MongoClient(
    dict(hots='localhost',
    port=27017)
)
db=client.get_database('test')


user_doc = Document[SysUser]()
user_doc.object.department= Departments()
user_doc.object.department.Code="Test"
user_doc.object.departments.append(Departments())
user_doc.object.add_department(Departments())
user_doc.object.department.CreatedOn = datetime.datetime.now()
f=user_doc.fields.Name==re.compile("^XX",re.IGNORECASE)
# fx=(1>f) & (f <=0.2) & (f>=1)&(f!=10)

print(f)
print(f.use_compare_or_logical_op)
print(f.use_math_op)



print(user_doc)
