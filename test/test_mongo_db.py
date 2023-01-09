import pymongo

client = pymongo.MongoClient(
    host="172.16.7.91",
    port=30271

)
coll = client.get_database("nttlong").get_collection("test")
for x in coll.find({}):
    print(x)
client.get_database("nttlong").get_collection("test").insert_one({
    "a": 123
})
print("OK")
#docker run mongo -d  --name mongo-on-docker  -p 27888:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=a1234
#docker run --name lv-test -d mongo -p 27888:27017 -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=a1234
#bindIp: 127.0.0.1
