"""
Đây là file  app để chạy api
Với môi trường dev hoặc chạy test
dùng windows command line
Chạy uvicorn api_app:app --reload
"""

import os
import sys
import pathlib

import uvicorn.server
import fasty
import uvicorn
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))
"""
Nạp môi trường 
"""
# from fastapi import FastAPI
#
# app = FastAPI()
import fasty
import pathlib
app = fasty.install_fastapi_app(__name__)


import fasty_api
"""
Napapi
"""
import fasty_pages
"""
Nap trang quan ly
"""
fasty.logger.logger.info("start in iis")

#uvicorn api_app:app --reload