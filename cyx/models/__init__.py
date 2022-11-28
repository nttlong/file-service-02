sys_messages_document_name = "Sys_messages_v2"
import datetime
import cy_docs
@cy_docs.define(
    name=sys_messages_document_name,
    indexes=["MsgType", "CreatedOn", "AppName", "MsgId"]
)
class SysMessage:
    """
    Message
    """
    MsgId: str
    AppName: str
    MsgType: str
    Data: str
    CreatedOn: datetime.datetime
    IsFinish: bool
    IsLock: bool
    InstancesLock: dict
    RunInsLock: str