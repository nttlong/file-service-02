import mimetypes
import cy_web
import cy_docs
import cy_xdoc
from pymongo import MongoClient
client = MongoClient(host="192.168.18.36",port=27018)
from cy_xdoc.models.files import FsFile
doc= cy_docs.context(client,FsFile)
expr= cy_docs.expr(FsFile)
for n in client.list_database_names():
    db_doc=doc[n]
    while db_doc.count(cy_docs.not_exists(expr.contentType)|cy_docs.is_null(expr.contentType))>0:
        items = db_doc.aggregate().match(cy_docs.not_exists(expr.contentType)).project(
            expr.contentType,
            expr.Id,
            expr.filename
        ).limit(1000)

        for x in items:
            m,_ = mimetypes.guess_type(x.filename.replace("..","."))
            print(x.filename)
            print(m)
            db_doc.update(
                expr.Id==x["_id"],
                expr.contentType << m
            )

    print(f"all data fixed {n}")

