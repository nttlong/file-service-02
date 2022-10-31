import datetime

import cy_docs
import asyncio
from pymongo.mongo_client import MongoClient

client = MongoClient(host="192.168.18.36", port=27018)
db_name = 'long-test-001'

test_docs = cy_docs.get_doc(
    "long-test",
    client,
    unique_keys=[
        "username"
    ]
)

agg = test_docs[db_name].aggregate().project(
    cy_docs.fields.username,
    (cy_docs.Funcs.concat (cy_docs.fields.username,'/',cy_docs.fields.password)>>cy_docs.fields.FullName),
    cy_docs.fields.create_on
).match(
    (cy_docs.fields.FullName== 'user991/password991') |
    (cy_docs.fields.username=="user100")
).sort(
    cy_docs.fields.create_on.desc()
)
for x in agg:
    print(x)
print(agg)
async def test():
    t1 = datetime.datetime.now()
    print(~cy_docs.Funcs.exists(cy_docs.fields.full_name))
    try:
        ret = await test_docs[db_name].insert_one_async(
            cy_docs.fields.username << f"user_1{100}",
            cy_docs.fields.depart_id << [1, 2, 3, 4]
        )
    except Exception as e:
        print(e)
    print(~((cy_docs.fields.age > 10) | (cy_docs.fields.username == 'root')))
    n = (datetime.datetime.now() - t1).total_seconds()

    print(n)
    # data = ret.to_json_convertable()
    return ret


# print("math parse")
# print(cy_docs.fields.num + 1)
# print(cy_docs.fields.num - 1)
# print(cy_docs.fields.num * 1)
# print(cy_docs.fields.num / 1)
# print(cy_docs.fields.num % 1)
# test_docs[db_name].update(
#     cy_docs.fields.username == f"user{100}",
#     cy_docs.fields.full_name << "test cai coi",
#     cy_docs.fields.first_name << "Julia",
#     cy_docs.fields.last_name << "petty",
# )
# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.create_task(test())
# loop.run_forever()
# t = datetime.datetime.now()

"""
Them 1000 doc
"""
# for x in range(0, 1000):
#     try:
#         test_docs[db_name] << (
#             cy_docs.fields.username << f"user{x}",
#             cy_docs.fields.password << f"password{x}",
#             cy_docs.fields.create_on << datetime.datetime.now(),
#         )
#     except Exception as e:
#         print(e)
# t = datetime.datetime.now()
# user_100 = test_docs[db_name] @ (cy_docs.Funcs.exists(cy_docs.fields.full_name))
# print(user_100)
# # for x in user_100:
# #     print(x)
# print((datetime.datetime.now() - t).total_seconds())
# print(user_100)
