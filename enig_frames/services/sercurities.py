import enig
from passlib.context import CryptContext
from jose import jwt

import enig_frames.config


class Sercurities(enig.Singleton):
    def __init__(self, config: enig_frames.config.Configuration = enig.depen(enig_frames.config.Configuration)):
        self.configuration: enig_frames.config.Configuration = config
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
