from pymodm.connection import connect

# c=connect("mongodb://test:test@localhost:27017/test","dddd")
from pymodm import MongoModel, fields
from pymongo.write_concern import WriteConcern

class User(MongoModel):
    email = fields.EmailField(primary_key=True)
    first_name = fields.CharField()
    last_name = fields.CharField()

    class Meta:
        write_concern = WriteConcern(j=True)

u=User('user@email.com', 'Bob', 'Ross')
import pymongo
client=pymongo.mongo_client.MongoClient("mongodb://test:test@localhost:27017/test")
db=client.get_database("XXX")
db.get_collection("Users").insert(
u.__dict__["_data"]._mongo_data
)
u.save()