"""
API liệt kê danh sách các file
"""
import ReCompact.dbm
import fasty
from fastapi import FastAPI, Request
import api_models.documents as docs
from ReCompact import db_async
import json

from . import api_files_schema


@fasty.api_post("/{app_name}/accounts/register")
async def register_new_account(app_name: str, request: Request):
    """
    Tạo một tài khoản truy cập vào application\n

    :param app_name:
    :return:
    """
    return dict(
        error=dict(
            code="NotImplemenet",
            message="Chua code"
        )
    )
