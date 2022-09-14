import datetime
import uuid

import flask_bcrypt
import pymongo.database
from werkzeug.security import generate_password_hash,check_password_hash
import api_models.Model_Users


def get_user_by_name(db:pymongo.database.Database,user_name:str)->dict:
    user_docs = api_models.Model_Users.User(db)
    ret = user_docs.find_one(user_docs.UsernameLowerCase==user_name.lower())
    return ret

def create_user(db:pymongo.database.Database,user:dict):
    user_docs= api_models.Model_Users.User(db)
    lowe_username = user[user_docs.Username.__name__].lower()
    user[user_docs.UsernameLowerCase.__name__]=lowe_username
    password: str = user[user_docs.Password.__name__]
    user[user_docs.Password.__name__]="*" #clear password
    pass_salt = str( uuid.uuid4())
    user[user_docs.PasswordSalt.__name__] =pass_salt
    user_str =f"{lowe_username};{password};{pass_salt}"
    print(user_str)
    user[user_docs.HashPassword.__name__] =generate_password_hash(user_str)
    user[user_docs.IsLocked.__name__] = False
    user[user_docs.CreatedOn.__name__] = datetime.datetime.now()


    user = user_docs.insert_one(user)
    return user

def check_user(db,username,password):
    user_docs = api_models.Model_Users.User(db)
    user = user_docs.find_one(
        user_docs.UsernameLowerCase==username.lower()
    )
    if not user:
        return user
    elif user.get(user_docs.IsLocked.__name__,False):
        return None
    else:
        has_password = user[user_docs.HashPassword.__name__]
        pass_salt = user[user_docs.PasswordSalt.__name__]

        is_ok = check_password_hash(has_password,f"{username.lower()};{password};{pass_salt}")
        if is_ok:
            return user
        else:
            return None