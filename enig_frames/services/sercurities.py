from datetime import datetime, timedelta

import enig
from passlib.context import CryptContext
from jose import jwt

import enig_frames.config
import enig_frames.services.applications
import enig_frames.repositories.accounts


class Sercurities(enig.Singleton):
    def __init__(self,
                 config: enig_frames.config.Configuration = enig.depen(
                     enig_frames.config.Configuration
                 ),
                 application_service: enig_frames.services.applications.Applications = enig.depen(
                     enig_frames.services.applications.Applications
                 ),
                 account_repo: enig_frames.repositories.accounts.Accounts = enig.depen(
                     enig_frames.repositories.accounts.Accounts
                 )):
        self.configuration: enig_frames.config.Configuration = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.application_service: enig_frames.services.applications.Applications = application_service
        self.account_repo: enig_frames.repositories.accounts.Accounts = account_repo

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, hash_data: str):
        return self.pwd_context.hash(hash_data)

    def decode_token(self, token):
        ret_data = jwt.decode(token, self.configuration.config.jwt.secret_key,
                              algorithms=[self.configuration.config.jwt.algorithm],
                              options={"verify_signature": False},
                              )
        return ret_data



    def create_access_token(self, app_name: str, username: str):
        ret = self.generate_access_token(
            data={
                "sub": username,
                "application": app_name
            },
            # expires_delta=self.configuration.config.jwt.access_token_expires

        )
        return ret

    def generate_access_token(self, data: dict, expires_delta=None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            self.configuration.config.jwt.secret_key,
            algorithm=self.configuration.config.jwt.algorithm)
        return encoded_jwt
