"""
Trường hợp DEv chạy để debug trên môi trường phát triển
"""
import sys

# from werkzeug import debug

import fasty
import pathlib

fasty.load_config(str(pathlib.Path(__file__).parent), "uvicorn.error")
import fasty.JWT

fasty.JWT.set_default_db(fasty.config.db.authSource)


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
        workers=2,
        debug=True,
        reload=True,

    )
