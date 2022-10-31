import datetime

import cy_docs
import asyncio
from pymongo.mongo_client import MongoClient
client = MongoClient(host="192.168.18.36",port=27018)
db_name ='long-test-001'

test_docs = cy_docs.get_doc(
    "long-test",
     client
)
async def test():
    t1= datetime.datetime.now()
    print(~cy_docs.Funcs.exists(cy_docs.fields.full_name))
    ret = await test_docs[db_name].find_one_async(cy_docs.Funcs.not_exists(cy_docs.fields.full_name)|(cy_docs.Funcs.is_null(cy_docs.fields.full_name)))
    print(~((cy_docs.fields.age >10)| (cy_docs.fields.username=='root')))
    n=(datetime.datetime.now()-t1).total_seconds()

    print(n)
    # data = ret.to_json_convertable()
    return ret
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(test())
loop.run_forever()
t=datetime.datetime.now()

"""
Them 1000 doc
"""
for x in range(0,1000):
    test_docs[db_name]<<(
        cy_docs.fields.username<<f"user{x}",
        cy_docs.fields.password<<f"password{x}",
        cy_docs.fields.create_on <<datetime.datetime.now(),
    )
t=datetime.datetime.now()
user_100 = test_docs[db_name]@(cy_docs.fields.username == f"user{100}")
print(user_100)
# for x in user_100:
#     print(x)
print((datetime.datetime.now()-t).total_seconds())
print(user_100)
