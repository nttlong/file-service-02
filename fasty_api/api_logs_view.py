"""
API liệt kê danh sách các file
"""
import datetime
import re
from time import strftime
from time import gmtime
import ReCompact.dbm

from fastapi import Request, Response
import api_models.documents as docs
from fastapi import Depends
from ReCompact import db_async

from . import api_files_schema
import fasty.JWT
from pathlib import Path
import enig_frames.containers
import enig_frames.services.applications
import enig_frames.containers

@fasty.api_post("/logs/views")
async def get_list_of_files(request: Request,
                            token: str = Depends(fasty.JWT.oauth2_scheme)):
    """
    APi này sẽ liệt kê danh sách các file
    :param filter:
    :param app_name:
    :return:
    """
    container= enig_frames.containers.Container
    ret = await container.db_log.get_top_logs_async(100)
    return ret

