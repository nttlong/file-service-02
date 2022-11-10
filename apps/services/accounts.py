import cy_kit
from apps.configs import Configs
import fastapi
class AccountsService:
    def __init__(self,config=cy_kit.single(Configs)):
        self.config = config
