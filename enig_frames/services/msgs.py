import datetime
import uuid

import api_models.documents
import enig
import enig_frames.db_context
from typing import List


class MessageInfo:
    def __init__(self):
        self.MsgType: str = None
        self.Data: dict = None
        self.CreatedOn: datetime.datetime = None
        self.AppName: str = None
        self.Id:str = None


class Message(enig.Singleton):
    def __init__(
            self,
            db=enig.depen(enig_frames.db_context.DbContext)
    ):
        self.db = db

    def emit(self, app_name: str, message_type: str, data: dict):
        self.db.context('admin').insert_one(
            api_models.documents.SysMessage,
            api_models.documents.SysMessage.MsgId==str(uuid.uuid4()),
            api_models.documents.SysMessage.MsgType == message_type,
            api_models.documents.SysMessage.Data == data,
            api_models.documents.SysMessage.CreatedOn == datetime.datetime.utcnow(),
            api_models.documents.SysMessage.IsFinish == False,
            api_models.documents.SysMessage.AppName == app_name
        )

    def get_message(self, message_type: str, max_items: int = 1000) -> List[MessageInfo]:
        ret_list = self.db.context('admin').aggregate(
            api_models.documents.SysMessage
        ).match(
            filter=api_models.documents.SysMessage.MsgType == message_type
        ).sort(
            api_models.documents.SysMessage.CreatedOn.asc()
        ).pager(
            page_size=max_items,
            page_index=0
        ).to_list()
        ret = []
        for x in ret_list:
            fx = MessageInfo()
            fx.MsgType = x.get(api_models.documents.SysMessage.MsgType.__name__)
            fx.Data = x.get(api_models.documents.SysMessage.Data.__name__)
            fx.AppName = x.get(api_models.documents.SysMessage.AppName.__name__)
            fx.CreatedOn = x.get(api_models.documents.SysMessage.CreatedOn.__name__)
            fx.Id = x.get(api_models.documents.SysMessage.MsgId.__name__)
            ret += [fx]
        return ret


    def delete(self, item:MessageInfo):
        self.db.context('admin').delete_one(
            api_models.documents.SysMessage,
            api_models.documents.SysMessage.MsgId==item.Id
        )
