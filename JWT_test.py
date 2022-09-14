from sqlalchemy.sql.functions import user

import fasty.JWT
import motor.motor_asyncio
fasty.JWT.set_connection_string("mongodb://localhost:27017")


password="123456"
has_pass= fasty.JWT.get_password_hash(password)
print(has_pass)
is_ok= fasty.JWT.verify_password(password,has_pass)
print(is_ok)
token= fasty.JWT.create_access_token(dict(
    Username="root",
    Email="XXXX1"
))
# fasty.JWT.create_user(
#     "long-test",
#     Username="root",
#     Password="root",Email="test1")
user=fasty.JWT.get_user_by_username("long-test","root")
print(user)
is_ok= fasty.JWT.authenticate_user("long-test","root","root")
user= fasty.JWT.get_current_user("long-test",token)
print(token)