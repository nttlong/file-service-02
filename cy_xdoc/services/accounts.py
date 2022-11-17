import datetime
import uuid

import cy_kit

from cy_xdoc.services.base import Base
import cy_docs
from cy_xdoc.models.users import User
from cy_xdoc.models.sso import SSO
from passlib.context import CryptContext


class AccountService(Base):
    def __init__(self):

        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, hash_data: str):
        return self.pwd_context.hash(hash_data)

    def validate(self, app_name, username: str, password: str):
        docs = cy_docs.expr(User)
        user = self.db(app_name).doc(User).find_one(
            docs.UsernameLowerCase == username.lower()
        )

        if user is None:
            return False
        if not self.verify_password(
                plain_password=username.lower() + "/" + password,
                hashed_password=user.HashPassword
        ):
            return False
        else:
            return True
        if user is None:
            return False
        else:
            return True

    def create_sso_id(self, app_name: str, token: str, return_url: str):
        doc = cy_docs.expr(SSO)
        sso_id = str(uuid.uuid4())
        ret = self.db('admin').doc(SSO).insert_one(
            doc.SSOID << sso_id,
            doc.ReturnUrlAfterSignIn << return_url,
            doc.CreatedOn << datetime.datetime.utcnow(),
            doc.Token << token
        )
        return sso_id

    def get_sso_login(self,id:str):
        doc = cy_docs.expr(SSO)
        ret =self.db('admin').doc(SSO).find_one(
            doc.SSOID==id
        )
        return ret