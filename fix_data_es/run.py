import sys
import pathlib

w_d = str(pathlib.Path(__file__).parent)
sys.path.append(w_d)

import enigma_docs


@enigma_docs.document_name(name="DocUploadRegister")
class DocUploadRegister:
    def __init__(self):
        self._id = None


from pymongo.mongo_client import MongoClient

client = MongoClient(
    host="192.168.18.36",
    port=27018
)

import enigma_docs


@enigma_docs.factory(client=client)
class Factory:
    doc_upload_register: enigma_docs.Document[DocUploadRegister]


ret = Factory.doc_upload_register.find(
    db_name="hps-file-test",
    filter=Factory.doc_upload_register.fields._id == None,

)

print(Factory.doc_upload_register.fields._id == None)

fx = list(ret)
print(fx)
