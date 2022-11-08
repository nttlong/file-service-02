import datetime
import json

import enig
import cy_docs
import asyncio
from pymongo.mongo_client import MongoClient

client = MongoClient(host="192.168.18.36", port=27018)
db_name = 'long-test-001'
import api_models.Model_Files
filter:api_models.Model_Files.DocUploadRegister =cy_docs.expr(api_models.Model_Files.DocUploadRegister)
print(filter.FileName==1)
class MyClass(enig.Singleton):
    def __init__(self,x=1):
        print(x)
        print("Create")
class B(enig.Singleton):
    def __init__(self,x=enig.depen(MyClass)):
        self.x=x
class C(enig.Singleton):
    def __init__(self,x=enig.depen(MyClass)):
        self.x=x

fd= enig.depen(C)
fy= enig.depen(B)
import enig_frames.config
s=enig.depen(enig_frames.config.Configuration)
print(fy.x)
import enig_frames.containers
container = enig_frames.containers.Container