import datetime
from typing import List
class MessageInfo:
    def __init__(self):
        self.MsgType: str = None
        self.Data: dict = None
        self.CreatedOn: datetime.datetime = None
        self.AppName: str = None
        self.Id:str = None
class MessageService:
    def emit(cls, app_name:str, message_type:str, data:dict):
        pass

    def get_message(self, message_type: str, max_items: int = 1000) -> List[MessageInfo]:
        pass


    def delete(self, item: MessageInfo):
        pass
    def reset_status(self,message_type:str):
        """
        Reset status
        :param message_type:
        :return:
        """
        raise NotImplemented

    def lock(self, item: MessageInfo):
        pass

    def unlock(self, item: MessageInfo):
        pass

    def is_lock(self, item: MessageInfo):
        pass
