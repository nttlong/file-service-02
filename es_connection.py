import quicky.yaml_reader
import pathlib
import os
import pymongo.mongo_client
elastic_yaml_path = os.path.join(str(pathlib.Path(__file__).parent.absolute()),"elastic.yaml")
es_config = quicky.yaml_reader.from_file(elastic_yaml_path)
from datetime import datetime
from elasticsearch import Elasticsearch
es_client = Elasticsearch(
    hosts=es_config["hosts"]
)
es_index = es_config["index"]

