import datetime
import os.path
import sys
import pathlib

w_d = str(pathlib.Path(__file__).parent)
sys.path.append(w_d)

import enigma_docs


@enigma_docs.document_name(name="DocUploadRegister")
class DocUploadRegister:
    def __init__(self):
        self._id = None
        self.HasIndexSearch = None
        self.MainFileId = None
        self.OCRFileId = None
        self.FileName = None
        """
        Neu co ORC
        """
@enigma_docs.document_name(name="fs.files")
class FSFile:
    def __init__(self):
        self._id=None




from pymongo.mongo_client import MongoClient

client = MongoClient(
    host="192.168.18.36",
    port=27018
)

import enigma_docs


@enigma_docs.factory(client=client)
class Factory:
    doc_upload_register: enigma_docs.Document[DocUploadRegister]
    files:enigma_docs.Document[FSFile]
    doc_upload_register_2:DocUploadRegister = DocUploadRegister()

fx = Factory.doc_upload_register









db_name = "hps-file-test"
import enig_frames.containers
container = enig_frames.containers.Container
for x in Factory.doc_upload_register.documents(db_name,Factory.doc_upload_register.fields.HasIndexSearch==None):

    print(x[Factory.doc_upload_register.fields.FileName])
    file_path=os.path.join('/home/vmadmin/python/v6/file-service-02/fix_data_es/files',x[Factory.doc_upload_register.fields.FileName])
    if os.path.isfile(file_path):
        print(f"da co {file_path}")
        pass
    try:
        ocr_file = Factory.files.document(db_name,
                                          Factory.files.fields._id == x[Factory.doc_upload_register.fields.OCRFileId])
        if ocr_file:
            enigma_docs.save_to_file(
                client,db_name,ocr_file[Factory.files.fields._id],file_path
            )
            print(f"ORC={ocr_file}")
        else:
            file = Factory.files.document(db_name,Factory.files.fields._id == x[Factory.doc_upload_register.fields.MainFileId])
            if file:
                enigma_docs.save_to_file(
                    client, db_name, file[Factory.files.fields._id], file_path
                )
    except Exception as e:
        print(e)
    if os.path.isfile(file_path):
        r:dict = x.to_json_compatible()
        container.Services.search_engine.make_index_content(
            app_name=db_name,
            upload_id= x[Factory.doc_upload_register.fields._id],
            file_path=file_path,
            data_item= r

        )
        Factory.doc_upload_register.update_one(
            db_name,Factory.doc_upload_register.fields._id==x[Factory.doc_upload_register.fields._id],
            {
                Factory.doc_upload_register.fields.HasIndexSearch.__name__: True
            }
        )

print("XONG")
