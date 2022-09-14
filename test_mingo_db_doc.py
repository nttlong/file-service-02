import datetime
import db_connection
import ReCompact.dbm.DbObjects
from ReCompact import document
from ReCompact.dbm.db_actions import __real_dict__,__real_dict_2__
# test=__real_dict__("a.b.c",1)
# test = __real_dict__({
#
#     "a.x":2,
#     "a.b.c":3
# })
db = db_connection.connection.get_database("test001")
# @document()

@document(
    name="Employees",
    keys=["IDCard"],
    indexes=["DepartmentCode","FirstName","LastName","BirthDate"]
)
class Person1:
    Code = (str,True,30)
    FirstName = (str,True)
    LastName = (str,True)
    BirthDate = (datetime.datetime)
    IDCard=(str)
class Person(Person1):
    Manager = Person1
class DepartmentClass:
    Code = (str,True)
    Name =(str,True)
    Emps= Person
@document(
    name="Employees",
    keys=["Code"],
    indexes=["DepartmentCode","FirstName","LastName","BirthDate"]
)
class Employees(Person):
    Department=(DepartmentClass)


person_docs = Employees(db)
# ff= test=__real_dict_2__(
#     # person_docs.Department.Emps.Code == float(0.1),
#     # person_docs.Code == "NV002",
#     # person_docs.Department.Code == "BP001",
#     # person_docs.Manager.IDCard == "ST001",
#     person_docs.Manager == (
#         person_docs.Manager.FirstName == "XXX",
#         person_docs.Manager.LastName == "XXX"
#
#     )
# )
# ff2= __real_dict_2__(ff)
# ff= test=__real_dict_2__(
#     {'Department.Emps.Code': 'AAA', 'Code': 'NV001', 'Department.Code': 'BP001'}
# )
# try:
person_docs.update_one(
    person_docs.Code=="NV002",
    person_docs.set(
        person_docs.Department.Code =="BP002",
        person_docs.Manager.at(0).Gender=="dsadad"
    )
)
person_docs.insert_one(
    person_docs.Code=="E001",
    person_docs.FirstName=="E001",
    person_docs.IDCard =="00001",
    person_docs.Department.Emps.Code=="AAA",
    person_docs.Code =="NV002",
    person_docs.Department.Code=="BP001",
    person_docs.Manager.IDCard =="ST001",
    person_docs.Manager==[(
        person_docs.Manager.FirstName=="XXX",
        person_docs.Manager.LastName=="XXX",
        person_docs.Manager.Gender==True

    )]

)

# except Exception as e:
#     print(e)
lst = list(person_docs)
print(lst)
print("OK")