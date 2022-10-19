from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,Request,Response
from fastapi.staticfiles import StaticFiles
import mimetypes
import enig
import enig_frames.config
import traceback
import enig_frames.loggers
import sys
class WebApp(enig.Singleton):
    def __init__(self,
                 configuration: enig_frames.config.Configuration =enig.depen(
                     enig_frames.config.Configuration
                 ),
                 loggers: enig_frames.loggers.Loggers = enig.depen(
                     enig_frames.loggers.Loggers
                 )):
        self.logger=loggers.get_logger(logger_name="web")
        self.configuration:enig_frames.config.Configuration = configuration
    def create_web_app(self,module_name):
        try:
            app = FastAPI()
            print(module_name)
            self.app = app
            setattr(sys.modules[module_name], "app", app)
            origins = ["*"]

            app.add_middleware(
                CORSMiddleware,
                allow_origins=origins,
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

            async def catch_exceptions_middleware(request: Request, call_next):
                try:
                    res = await call_next(request)
                    if request.url.path.endswith('.js') and '/static/' in request.url.path:
                        t, _ = mimetypes.guess_type(request.url.path)
                        res.headers['content-type'] = t

                    return res
                except Exception as e:
                    self.logger.exception(traceback.format_exc())
                    # you probably want some kind of logging here
                    return Response("Internal server error", status_code=500)

            app.middleware(self.configuration.config.host_schema)(catch_exceptions_middleware)
            app.mount("/static", StaticFiles(directory=self.configuration.static_dir), name="static")
            return app

        except Exception as e:
            self.logger.exception(traceback.format_exc())
            print(traceback.format_exc())
