"""
Trường hợp DEv chạy để debug trên môi trường phát triển
"""
from werkzeug import debug

import fasty
import pathlib
fasty.load_config(str(pathlib.Path(__file__).parent),"uvicorn.error")
import fasty.JWT
fasty.JWT.set_default_db(fasty.config.db.authSource)

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "api_app:app",
        host=fasty.config.host.binding.ip,
        port=fasty.config.host.binding.port,
        workers=2,
        debug=True,
        reload=True,

    )