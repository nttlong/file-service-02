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
print("-----port--------------")
print(os.getenv('file_server_bind_port'))
sys.path.append(str(pathlib.Path(__file__).parent.parent.absolute()))
"""
Nạp môi trường 
"""
# from fastapi import FastAPI
#
# app = FastAPI()
print('ok run')
import fasty

fasty.load_config(str(pathlib.Path(__file__).parent), "uvicorn.error")
import fasty.JWT as fjwt
fjwt.set_default_db(fasty.config.db.authSource)




db_server = os.environ.get('LV_API_DEFAULT_DB','lv-docs')
if db_server is not None:
    import fasty.JWT
    fasty.JWT.set_default_db(db_server)
print(db_server)
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