
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import cy_web

cy_web.create_web_app(
    working_dir=pathlib.Path(__file__).parent.__str__(),
    static_dir="./../app_manager/static",
    template_dir="./../app_manager/html",
    host_url="http://172.16.13.72:8013",
    bind="0.0.0.0:8013",
    cache_folder="./cache",
    dev_mode= True,

)
cy_web.add_cors(["*"])


cy_web.load_controller_from_dir("api","./controllers")
cy_web.load_controller_from_dir("","./pages")
if __name__ == "__main__":
    cy_web.start_with_uvicorn(worker=1)