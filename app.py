
import quicky

import mimetypes
from flask import Flask
from quicky.config import Config
import pathlib
import sys

app_config = Config(str(pathlib.Path(__file__).parent))

# import routes.api_file_upload
mimetypes.types_map[".js"]="text/javascript"
mimetypes.types_map[".docx"]="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
mimetypes.types_map[".avif"]="image/avif"
app = quicky.QuickyApp(
    __name__,
    app_config
)

@app.after_request
def after_request_callback( response ):
    # your code here
    if response.mimetype=="text/javascript":
        response.status=200
    return response
import quicky

import url
if __name__ == '__main__':
    app_config.logger.info("------------------------------------------------------")
    app_config.logger.info("web start with:")
    app_config.logger.info(dict(debug=app_config.debug, host=app_config.host, port=app_config.port))
    app_config.logger.info("------------------------------------------------------")
    app.run(
          debug=app_config.debug,
          host= app_config.host,
          port=app_config.port,
          threaded=True
    )


#C:\dj-apps-2022-05-25\jd-apps\venv\Scripts\python.exe C:\dj-apps-2022-05-25\jd-apps\app.py
#C:\code\python\jd-apps\venv\Scripts\python.exe C:\code\python\jd-apps\app.py