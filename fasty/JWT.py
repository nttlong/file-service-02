"""
Quản lý JWT
"""
import threading


from typing import Any, Dict, List, Optional, Union
from fastapi.exceptions import HTTPException
from fastapi.openapi.models import OAuth2 as OAuth2Model
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.param_functions import Form
from fastapi.security.base import SecurityBase
from fastapi.security.utils import get_authorization_scheme_param
from starlette.requests import Request
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_301_MOVED_PERMANENTLY
import bson
from fastapi_jwt_auth import AuthJWT

import enig
import enig_frames.services.sercurities
import fasty
from . import JWT_Docs
from datetime import datetime, timedelta
from typing import Union
import asyncio
import ReCompact.db_async
import motor
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import jose


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"
    # Configure application to store and get JWT from cookies
    authjwt_token_location: set = {"cookies"}
    # Disable CSRF Protection for this example. default is True
    authjwt_cookie_csrf_protect: bool = False


@AuthJWT.load_config
def get_config():
    return Settings()


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
USER_COLLECTION_NAME = "sys_jwt_users"
CONNECTION_STRING = None
__default_db__ = None


def set_default_db(value):
    global __default_db__
    __default_db__ = value


class TokenData(BaseModel):
    username: Union[str, None] = None
    application: Union[str, None] = None
import enigma

def get_token_url():

    __api_host_dir__ = enigma.app_config.get_config('api_host_dir')
    if __api_host_dir__ is None:
        raise Exception("Please call fasty.JWT.set_api_host_dir at start application")
    ret = "/accounts/token"
    if __api_host_dir__ != "":
        ret = __api_host_dir__ + "/accounts/token"
    return ret


__oauth2_scheme__ = None
__oauth2_scheme_anonymous__ = None


class OAuth2Redirect(OAuth2PasswordBearer):
    def __init__(
            self,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            auto_error: bool = True,
    ):
        tokenUrl = get_token_url()
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            tokenUrl=tokenUrl,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
            scopes=scopes
        )

    async def __call__(self, request: Request) -> Optional[str]:

        if request.cookies.get('access_token_cookie', None) is not None:
            token = request.cookies['access_token_cookie']
            try:
                ret_data = jwt.decode(token, enigma.app_config.get_config('jwt')['secret_key'],
                                      algorithms=[enigma.app_config.get_config('jwt')['algorithm']],
                                      options={"verify_signature": False},
                                      )

                setattr(request, "usernane", ret_data.get("sup"))
                setattr(request, "application_name", ret_data.get("app"))

                return token
            except jose.exceptions.ExpiredSignatureError as e:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            authorization: str = request.headers.get("Authorization")
            scheme, token = get_authorization_scheme_param(authorization)
            if not authorization or scheme.lower() != "bearer":
                if self.auto_error:
                    raise HTTPException(
                        status_code=HTTP_301_MOVED_PERMANENTLY,
                        detail="Not authenticated dasd",
                        headers={"Location": "login"},
                    )
                else:
                    return None
            try:
                ret_data = jwt.decode(token,enigma.app_config.get_config('jwt').get('secret_key'),
                                      algorithms=[enigma.app_config.get_config('jwt').get('algorithm')],
                                      options={"verify_signature": False},
                                      )

                setattr(request, "usernane", ret_data.get("sup"))
                setattr(request, "application_name", ret_data.get("application"))
            except jose.exceptions.JWTError:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except jose.exceptions.ExpiredSignatureError as e:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return token


class OAuth2PasswordBearerAndCookie(OAuth2PasswordBearer):
    def __init__(
            self,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            auto_error: bool = True,
    ):
        tokenUrl = get_token_url()
        if not scopes:
            scopes = {}
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl, "scopes": scopes})
        super().__init__(
            tokenUrl=tokenUrl,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
            scopes=scopes
        )

    async def __call__(self, request: Request) -> Optional[str]:
        if request.cookies.get('access_token_cookie', None) is not None:
            token = request.cookies['access_token_cookie']
            try:
                sercurity_services= enig.depen(enig_frames.services.sercurities.Sercurities)
                ret_data=sercurity_services.decode_token(token)

                setattr(request, "usernane", ret_data.get("sup"))
                setattr(request, "application_name", ret_data.get("application"))
                return token
            except jose.exceptions.ExpiredSignatureError as e:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            authorization: str = request.headers.get("Authorization")
            scheme, token = get_authorization_scheme_param(authorization)
            if not authorization or scheme.lower() != "bearer":
                if self.auto_error:
                    raise HTTPException(
                        status_code=HTTP_401_UNAUTHORIZED,
                        detail="Not authenticated",
                        headers={"WWW-Authenticate": "Bearer"},
                    )
                else:
                    return None
            try:
                ret_data = jwt.decode(token, enigma.app_config.get_config('jwt').get('secret_key'),
                                      algorithms=[enigma.app_config.get_config('jwt').get('algorithm')],
                                      options={"verify_signature": False},
                                      )

                setattr(request, "usernane", ret_data.get("sup"))
                setattr(request, "application_name", ret_data.get("application"))
            except jose.exceptions.JWTError:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            except jose.exceptions.ExpiredSignatureError as e:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return token


class OAuth2PasswordBearerAndCookieWithAnonymous(OAuth2PasswordBearer):
    def __init__(
            self,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            auto_error: bool = True,
    ):
        tokenUrl = get_token_url()
        if not scopes:
            scopes = {}

        super().__init__(
            tokenUrl=tokenUrl,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
            scopes=scopes
        )

    async def __call__(self, request: Request) -> Optional[str]:
        if request.cookies.get('access_token_cookie', None) is not None:
            token = request.cookies['access_token_cookie']
            return token
        else:
            authorization: str = request.headers.get("Authorization")
            scheme, token = get_authorization_scheme_param(authorization)

            return token


def get_oauth2_scheme():
    global __oauth2_scheme__
    if __oauth2_scheme__ is None:
        __oauth2_scheme__ = OAuth2PasswordBearerAndCookie()
    return __oauth2_scheme__


def get_oauth2_scheme_anonymous():
    global __oauth2_scheme_anonymous__
    if __oauth2_scheme_anonymous__ is None:
        __oauth2_scheme_anonymous__ = OAuth2PasswordBearerAndCookieWithAnonymous()
    return __oauth2_scheme_anonymous__


def set_connection_string(cnn: str):
    global CONNECTION_STRING
    CONNECTION_STRING = cnn
    ReCompact.db_async.set_connection_string(cnn)





def sync(*args, **kwargs):
    """
    Khử sync
    :param args:
    :param kwargs:
    :return:
    """
    loop = asyncio.get_event_loop()
    coroutine = args[0]
    ret = loop.run_until_complete(coroutine)
    return ret


async def get_user_by_username_async(db_name: str, username: str):


    dbcntx = ReCompact.db_async.get_db_context(db_name)
    user = await dbcntx.find_one_async(JWT_Docs.Users, JWT_Docs.Users.UsernameLowerCase == username.lower())
    return user


def get_user_by_username(db_name: str, username: str):
    return sync(get_user_by_username_async(db_name, username))


async def get_user_by_user_id_async(db_name: str, user_id: str):


    dbcntx = ReCompact.db_async.get_db_context(db_name)
    user = await dbcntx.find_one_async(JWT_Docs.Users, JWT_Docs.Users._id == bson.ObjectId(user_id))
    return user


def get_user_by_user_id(db_name: str, username: str):
    return sync(get_user_by_user_id_async(db_name, username))


async def create_user_async(db_name: str, Username: str, Password: str, Email: str, IsSysAdmin: bool = False):


    dbcntx = ReCompact.db_async.get_db_context(db_name)

    UsernameLower = Username.lower()
    HashPassword = get_password_hash(UsernameLower + "/" + Password)
    try:
        ret_user = await dbcntx.insert_one_async(
            JWT_Docs.Users,
            JWT_Docs.Users.Username == Username,
            JWT_Docs.Users.UsernameLowerCase == UsernameLower,
            JWT_Docs.Users.Email == Email,
            JWT_Docs.Users.HashPassword == HashPassword,
            JWT_Docs.Users.IsLocked == False,
            JWT_Docs.Users.CreatedOnUTC == datetime.now(),
            JWT_Docs.Users.CreatedOn == datetime.utcnow(),
            JWT_Docs.Users.IsSysAdmin == IsSysAdmin

        )
    except ReCompact.db_async.Error as e:
        if e.code == ReCompact.db_async.ErrorType.DUPLICATE_DATA:
            if (set([
                JWT_Docs.Users.Username.__name__,
                JWT_Docs.Users.UsernameLowerCase.__name__]) & set(e.fields)).__len__() > 0:
                e.message = "User is already"
            if (set([
                JWT_Docs.Users.Email.__name__]) & set(e.fields)).__len__() > 0:
                e.message = "Email is already"
        raise e


def create_user(db_name: str, Username: str, Password: str, Email: str):
    return sync(create_user_async(db_name, Username, Password, Email))


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Union[str, None] = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearerAndCookie()


def verify_password(plain_password, hashed_password):
    global pwd_context
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user_async(app_name: str, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get(JWT_Docs.Users.Username.__name__, payload.get('sub'))
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        fx = 1
        raise credentials_exception
    db_name = await get_db_name_async(app_name)
    user = await get_user_by_username_async(db_name, token_data.username)
    user["Id"] = user["_id"]
    user["username"] = user[JWT_Docs.Users.UsernameLowerCase.__name__]
    if user is None:
        return user
    return dict(
        UserId=user["Id"],
        Username=user[JWT_Docs.Users.Username.__name__],
        Email=user[JWT_Docs.Users.Email.__name__]
    )


def get_current_user(app_name: str, token: str = Depends(oauth2_scheme)):
    import asyncio
    loop = asyncio.get_event_loop()
    coroutine = get_current_user_async(app_name, token)
    ret = loop.run_until_complete(coroutine)
    return ret


async def get_current_active_user_async(current_user=Depends(get_current_user_async)):
    if current_user.get(JWT_Docs.Users.IsLocked.__name__):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def authenticate_user_async(app_name, username: str, password: str):
    global __default_db__
    if app_name == __default_db__:
        admin_db_context = ReCompact.db_async.get_db_context(app_name)
        root_admin_user = await admin_db_context.find_one_async(JWT_Docs.Users, JWT_Docs.Users.Username == "root")
        if root_admin_user is None:
            root_admin_user = await create_user_async(
                db_name=app_name,
                Username="root",
                Password="root",
                Email="root@local.com"
            )
    user = await get_user_by_username_async(app_name, username)
    if not user:
        return False
    if not verify_password(username.lower() + "/" + password, user[JWT_Docs.Users.HashPassword.__name__]):
        return False
    return user


def authenticate_user(app_name, username: str, password: str):
    return sync(authenticate_user_async(app_name, username, password))
__cache_app_info__ ={}
__lock_cache_app_info__ =threading.Lock()
__cache_db_name__ = {}
__lock_cache_db_name__ = threading.Lock()
async def get_db_name_async(app_name):
    global __cache_db_name__
    global __default_db__
    global __lock_cache_db_name__
    if __default_db__ is None:
        __default_db__ =enigma.app_config.get_config('admin_db_name')
    import fasty
    if app_name == "admin":
        return __default_db__
    else:
        ret = __cache_db_name__.get(app_name)
        if ret is not None:
            return ret
        import api_models.documents
        import ReCompact.db_async
        dbctx = ReCompact.db_async.get_db_context(__default_db__)
        ret = await dbctx.find_one_async(api_models.documents.Apps, api_models.documents.Apps.Name == app_name.lower())
        if ret is None:
            return ret
        else:
            __lock_cache_db_name__.acquire()
            __cache_db_name__[app_name]=app_name
            __lock_cache_db_name__.release()
            return app_name


async def get_app_info_async(app_name):
    global __default_db__
    if __default_db__ is None:
        raise Exception("Please call fasty.JWT.set_default_db when start application")
    import fasty
    if app_name == "admin":
        return __default_db__
    else:
        ret= __cache_app_info__.get(app_name)
        if ret is not None:
            return ret

        import api_models.documents
        import ReCompact.db_async
        dbctx = ReCompact.db_async.get_db_context(__default_db__)
        ret = await dbctx.find_one_async(api_models.documents.Apps, api_models.documents.Apps.Name == app_name.lower())
        __lock_cache_app_info__.acquire()
        __cache_app_info__[app_name]=ret
        __lock_cache_app_info__.release()
        return ret
