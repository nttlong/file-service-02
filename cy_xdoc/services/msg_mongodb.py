import datetime
import uuid
from _testcapi import matmulType

import cy_docs
import cy_kit
from cy_xdoc.services.msg import MessageService
from cy_xdoc.services.base import Base
from cy_xdoc.models.files import SysMessage

@cy_kit.must_imlement(MessageService)
class MessageServiceMongodb(Base):
    def emit(self, app_name: str, message_type: str, data: dict):
        doc = cy_docs.expr(SysMessage)
        self.db(app_name).doc(SysMessage).insert_one(
            doc.Data<<data,
            doc.MsgId<<str(uuid.uuid4()),
            doc.AppName<<app_name,
            doc.MsgType<<message_type,
            doc.CreatedOn<<datetime.datetime.utcnow()
        )
