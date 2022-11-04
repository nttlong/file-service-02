import datetime
import os.path
import pathlib
import uuid

import bson

import api_models.documents
import enig
import enig_frames.db_context
from typing import List
import re

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
        self.instance_id = str(uuid.uuid4())
        self.working_dir=pathlib.Path(__file__).parent.parent.parent.__str__()
        self.lock_dir = os.path.join(self.working_dir,"background_service_files","msg_lock")
        if not os.path.isdir(self.lock_dir):
            os.makedirs(self.lock_dir,exist_ok=True)
        files = list(list(os.walk(self.lock_dir))[0][2])
        val_id = None
        UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
        for x in files:
            file_name = pathlib.Path(x).stem
            if UUID_PATTERN.match(file_name):
                val_id = file_name
                break
        if val_id is None:
            with open(os.path.join(self.lock_dir,self.instance_id),'wb') as f:
                f.write(self.instance_id.encode('utf8'))
        else:
            self.instance_id = val_id



    def emit(self, app_name: str, message_type: str, data: dict):
        self.db.context('admin').insert_one(
            api_models.documents.SysMessage,
            api_models.documents.SysMessage.MsgId==str(uuid.uuid4()),
            api_models.documents.SysMessage.MsgType == message_type,
            api_models.documents.SysMessage.Data == data,
            api_models.documents.SysMessage.CreatedOn == datetime.datetime.utcnow(),
            api_models.documents.SysMessage.IsFinish == False,
            api_models.documents.SysMessage.AppName == app_name,
            api_models.documents.SysMessage.InstancesLock=={
                self.instance_id:True
            }
        )

    def get_message(self, message_type: str, max_items: int = 1000) -> List[MessageInfo]:
        import py_docs
        ret_list = self.db.context('admin').aggregate(
            api_models.documents.SysMessage
        ).match(
            filter=
            {
                "$and":[
                    {"MsgType":message_type},
                    {
                      "$or":[
                          {"RunInsLock":{"$exists":False}},
                          {"RunInsLock":{"$ne":self.instance_id}}
                      ]
                    }]
            }
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
            self.db.context('admin').update_one(
                api_models.documents.SysMessage,
                api_models.documents.SysMessage._id==bson.ObjectId(x["_id"]),
                api_models.documents.SysMessage.RunInsLock==self.instance_id
            )
        return ret


    def delete(self, item:MessageInfo):
        self.db.context('admin').delete_one(
            api_models.documents.SysMessage,
            api_models.documents.SysMessage.MsgId==item.Id
        )
