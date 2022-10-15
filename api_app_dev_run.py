import enigma
import sys

# from werkzeug import debug

import fasty
import pathlib
# fasty.load_config(str(pathlib.Path(__file__).parent), "uvicorn.error")
import fasty.JWT


import os
import uvicorn


if __name__ == "__main__":

    uvicorn.run(
        "api_app:app",
        host=enigma.app_config.get_config('binding_ip'),
        port=enigma.app_config.get_config('binding_port'),
        workers=1,
        ws='websockets',
        ws_max_size=16777216*1024,
        backlog=1000,
        # interface='WSGI',
        timeout_keep_alive=True,
        lifespan='on',

        debug=True,
        # reload=False,

    )
