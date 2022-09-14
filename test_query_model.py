import datetime
import motor.motor_asyncio
import motor
import asyncio
import db_connection
import ReCompact.db_async
import json
import api_models.documents
import ReCompact.dbm
import pymongo.mongo_client
import bson
import api_models.Model_Files
import re
@ReCompact.document("test",keys=["Code"])
class test:
    _id=(bson.ObjectId)
    Code=(str,True)
    Name=(str,True)
test_doc=test()
db = db_connection.connection.get_database("lv-docs")
ret_del=ReCompact.db_async.delete_many(db,test_doc,test_doc.Code=="XX")
ReCompact.db_async.update_one(db,test_doc,
                                test_doc.Code=="XX",
                              (
                                  test_doc.Code=="XXY",
                                  test_doc.Name=="sdadasdas",
                                  test_doc.Code=="YYY")
)
# list_of_files = ReCompact.db_async.find(
#     db,
#     api_models.documents.Files,
#     api_models.documents.Files.FileExt==re.compile("mp4")
# )
# txt= json.dumps(list_of_files)

