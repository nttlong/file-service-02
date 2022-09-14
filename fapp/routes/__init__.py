from flask import Flask  #importing flask elements to make everything work
import mimetypes
import quicky.config
import quicky.logs
import pathlib
mimetypes.types_map[".js"]="text/javascript"
app_config = quicky.config.Config(pathlib.Path(__file__).parent.parent)
app = Flask(
    __name__,
    static_folder= app_config.full_static_dir,
    static_url_path=app_config.static_url,
    template_folder= app_config.full_template_path
)
@app.after_request
def after_request_callback( response ):
    # your code here
    if response.mimetype=="text/javascript":
        response.status=200
    return response