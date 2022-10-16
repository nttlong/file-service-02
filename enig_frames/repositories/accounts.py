from datetime import datetime

import enig
import enig_frames.db_context
import api_models.documents
class Accounts(enig.Singleton):
    def __init__(self,db=enig.depen(enig_frames.db_context.DbContext)):
        self.db:enig_frames.db_context.DbContext=db

    def get_user_by_username(self, app_name:str, username:str):
        dbc=self.db.context(app_name)
        ret= dbc.find_one(
            api_models.documents.Users,
            api_models.documents.Users.UsernameLowerCase==username.lower()
        )
        return ret

    async def get_user_by_username_async(self, app_name:str, username:str):
        dbc=self.db.context(app_name)
        ret= await dbc.find_one_async(
            api_models.documents.Users,
            api_models.documents.Users.UsernameLowerCase==username.lower()
        )
        return ret

    def create(self, app_name:str, username:str,email:str,is_sys_admin:bool, hash_password):
        dbctx=self.db.context(app_name)
        ret_user = dbctx.insert_one(
            api_models.documents.Users,
            api_models.documents.Users.Username == username,
            api_models.documents.Users.UsernameLowerCase == username.lower(),
            api_models.documents.Users.Email == email,
            api_models.documents.Users.HashPassword == hash_password,
            api_models.documents.Users.IsLocked == False,
            api_models.documents.Users.CreatedOnUTC == datetime.now(),
            api_models.documents.Users.CreatedOn == datetime.utcnow(),
            api_models.documents.Users.IsSysAdmin == is_sys_admin

        )
