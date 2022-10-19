import os.path
import pathlib

import enig
import enig_frames.config


class Hosts(enig.Singleton):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(enig_frames.config.Configuration)):
        self.configuration: enig_frames.config.Configuration = configuration
        self.working_folder = str(pathlib.Path(__file__).parent.parent)
        self.tmp_upload_dir = self.configuration.config.tmp_upload_dir

        if self.tmp_upload_dir[0:2] == "./":
            self.tmp_upload_dir = os.path.join(self.working_folder, self.tmp_upload_dir[2:])

    @property
    def root_url(self) -> str:
        ret = f"{self.schema}://{self.name}"
        if self.port is not None:
            ret = f"{ret}:{self.port}"
        return ret

    @property
    def port(self):
        return self.configuration.config.host_port

    @property
    def schema(self) -> str:
        return self.configuration.config.host_schema

    @property
    def name(self):
        return self.configuration.config.host_name

    @property
    def api_host_dir(self):
        return self.configuration.config.api_host_dir

    @property
    def root_api_url(self) -> str:
        return f"{self.root_url}/{self.api_host_dir}"

    def get_temp_upload_dir(self, app_name: str):
        ret = os.path.join(self.tmp_upload_dir, app_name)
        if not os.path.isdir(ret):
            os.makedirs(ret)
        return ret
