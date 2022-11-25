from pymongo import MongoClient

import cy_docs
import cy_kit
import cy_web
from cy_xdoc.services.files import FileServices
from cy_xdoc.models.files import DocUploadRegister,FsFile
file:FileServices= cy_kit.singleton(FileServices)

doc = file.db_connect.db("lv-docs").doc(FsFile)
import mimetypes
for x in doc.context.find(cy_docs.not_exists(cy_docs.fields.contentType)):
    c, _ = mimetypes.guess_type(x["filename"])
    doc.context.update(
        doc.fields._id ==x["_id"],
        doc.fields.contentType<<c
    )
    print(x)