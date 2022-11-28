
import pathlib
import sys
sys.path.append(pathlib.Path(__file__).parent.parent.__str__())
import fastapi
import datetime
import cy_kit
import cyx.common

import cy_web

cy_web.create_web_app(
    working_dir=pathlib.Path(__file__).parent.__str__(),
    static_dir="./../resource/static",
    template_dir="./../resource/html",
    host_url="http://172.16.13.72:8011",
    bind="0.0.0.0:8011",
    cache_folder="./cache",
    dev_mode= cyx.common.config.debug,

)
import asyncio
cy_web.add_cors(["*"])
@cy_web.middleware()
async def estimate_time(request:fastapi.Request,next):
    start_time= datetime.datetime.utcnow()
    res = await next(request)
    end_time = datetime.datetime.utcnow()
    res.headers["time:start"] = start_time.strftime("%H:%M:%S")
    res.headers["time:end"] = end_time.strftime("%H:%M:%S")
    res.headers["time:total(second)"] = (end_time-start_time).total_seconds().__str__()
    res.headers["Server-Timing"] =f"total;dur={(end_time - start_time).total_seconds()*1000}"
    """HTTP/1.1 200 OK

Server-Timing: miss, db;dur=53, app;dur=47.2"""
    return res

cy_web.load_controller_from_dir("api","./controllers")
cy_web.load_controller_from_dir("","./pages")
if __name__ == "__main__":
    cy_web.start_with_uvicorn(worker=2)