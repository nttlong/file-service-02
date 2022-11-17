import cy_kit
from cy_xdoc.services.base import Base, DbClient


class MsgService(Base):


    def emit(self, app_name, message_type, data):
        pass
