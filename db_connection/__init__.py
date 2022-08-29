import quicky.yaml_reader
import pathlib
import os
import pymongo.mongo_client
database_yaml_path = os.path.join(str(pathlib.Path(__file__).parent.parent.absolute()),"database.yaml")
db_config = quicky.yaml_reader.from_file(database_yaml_path)
default_db_name=db_config["authSource"]
if db_config.get("replicaSet",None) is not None:
    connection = pymongo.mongo_client.MongoClient(

        host=db_config["host"],
        port=db_config["port"],
        username=db_config["username"],
        password=db_config["password"],
        authSource=db_config["authSource"],
        authMechanism=db_config["authMechanism"],
        replicaSet=db_config["replicaSet"]



    )
else:
    connection = pymongo.mongo_client.MongoClient(

        host=db_config["host"],
        port=db_config["port"],
        username=db_config["username"],
        password=db_config["password"],
        authSource=db_config["authSource"],
        authMechanism=db_config["authMechanism"]
    )
