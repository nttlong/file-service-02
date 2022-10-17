import enigma
import enig
import enig_frames.config
import sys

# from werkzeug import debug

import fasty
import pathlib
# fasty.load_config(str(pathlib.Path(__file__).parent), "uvicorn.error")
import fasty.JWT


import os
import uvicorn
configuration:enig_frames.config.Configuration = enig.create_instance(enig_frames.config.Configuration)

if __name__ == "__main__":

    uvicorn.run(
        "api_app:app",
        host=configuration.config.binding_ip,
        port=configuration.config.binding_port,
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
