import asyncio
import ReCompact.dbm.DbObjects
from ReCompact.dbm.DbObjects.Docs import Fields
import models
fields = Fields()
print((ReCompact.dbm.DbObjects.Filter.Code=='aaa').to_mongodb())
fx=  models.User(
    UserName="123"
)
import pymongo
cnn= pymongo.mongo_client.MongoClient(
    host="localhost",
    port=27017
)
db=cnn.get_database("long_test")
ret=ReCompact.dbm.DbObjects.find_to_objects_async(db,models.User,
                                 ReCompact.dbm.DbObjects.Filter.UserName=="123")
print(ret)
agg = ReCompact.dbm.DbObjects.aggregrate(db,models.User)
for x in list(agg):
    print(x)
