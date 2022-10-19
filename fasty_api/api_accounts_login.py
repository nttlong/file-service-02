"""
API liệt kê danh sách các file
"""
import ReCompact.dbm
import enig
import enig_frames.services.accounts

import fasty
from fastapi import FastAPI, Request, Response
import api_models.documents as docs
from ReCompact import db_async
import json
import fasty.JWT
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi_jwt_auth import AuthJWT

import enig_frames.containers

class Token(BaseModel):
    access_token: str




@fasty.api_post("/accounts/token", response_model=Token)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        Authorize: AuthJWT = Depends()
):
    container = enig_frames.containers.Container
    username = form_data.username
    app_name = ""
    if '/' in form_data.username:
        items = form_data.username.split('/')
        app_name = items[0]
        username = form_data.username[app_name.__len__() + 1:]
    elif '@' in form_data.username:
        items = form_data.username.split('@')
        app_name = items[-1]
        username = form_data.username[0:-app_name.__len__() - 1]
    db_name = container.db_context.get_db_name(app_name)



    if db_name is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Someting wrong, maybe incorrect domain",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await container.Services.accounts.authenticate_user_async(app_name,username,form_data.password)
    # user = await fasty.JWT.authenticate_user_async(db_name, username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token=  container.Services.security.create_access_token(
        app_name=app_name,
        username=username
    )
    # access_token_expires = timedelta(minutes=fasty.configuration.app.jwt.access_token_expire_minutes)
    # access_token = fasty.JWT.create_access_token(
    #     data={
    #         "sub": user[fasty.JWT.JWT_Docs.Users.Username.__name__],
    #         "application": app_name
    #     },
    #     # expires_delta=access_token_expires
    #
    # )
    # Create the tokens and passing to set_access_cookies or set_refresh_cookies
    # access_token = Authorize.create_access_token(subject=username)
    # refresh_token = Authorize.create_refresh_token(subject=username)

    # Set the JWT cookies in the response
    Authorize.set_access_cookies(access_token)
    # Authorize.set_refresh_cookies(refresh_token)
    return {"access_token": access_token, "token_type": "bearer"}
