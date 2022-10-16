import enig
from passlib.context import CryptContext

class Sercurities(enig.Singleton):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)
    def get_password_hash(self, hash_data:str):
        return self.pwd_context.hash(hash_data)