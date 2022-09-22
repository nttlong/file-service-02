"""
Trường hợp DEv chạy để debug trên môi trường phát triển
"""
"""
export file_server_use_os_config=true
export file_server_db_host=192.168.18.36
export file_server_db_port=27017
export file_server_db_auth_source=lv-docs
export file_server_db_replica_set =''
export file_server_db_username =admin-doc
export file_server_db_password =123456
"""
import os
os.environ['file_server_use_os_config']='1'

os.environ['file_server_db_host']='192.168.18.36'
os.environ['file_server_db_port']='27018'
os.environ['file_server_db_auth_source']='lv-docs'
os.environ['file_server_db_replica_set'] =''
os.environ['file_server_db_username'] ='admin-doc'
os.environ['file_server_db_password'] ='123456'
os.environ['file_server_bind_port']='8011'
os.environ['file_server_root_url']='http://172.16.13.72:8011'
os.environ['file_server_api_url']='http://172.16.13.72:8011/api'
os.environ['file_server_es_url']='http://192.168.18.36:9200,'
import sys

# from werkzeug import debug

import fasty
import pathlib

fasty.load_config(str(pathlib.Path(__file__).parent), "uvicorn.error")
import fasty.JWT

fasty.JWT.set_default_db(fasty.config.db.authSource)
import os

def get_arg_value(key,df_v=None):
    if key in sys.argv:
        i = sys.argv.index(key)
        if i + 1 < sys.argv.__len__():
            return sys.argv[i + 1]
    return df_v


import uvicorn
args = " ".join(sys.argv)
print(f"run with {args}")
port =int(get_arg_value("--port",fasty.config.host.binding.port))
print(str(port))


if __name__ == "__main__":

    uvicorn.run(
        "api_app:app",
        host=fasty.config.host.binding.ip,
        port=port,
        workers=1,
        ws='websockets',
        ws_max_size=16777216*1024,
        backlog=1000,
        # interface='WSGI',
        timeout_keep_alive=True,
        lifespan='on'

        # debug=False,
        # reload=False,

    )
