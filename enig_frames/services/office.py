import os
import pathlib

import enig
import enig_frames.config
from moviepy.editor import *
from matplotlib import pyplot as plt
from PIL import Image
import io
import uuid
import shutil
from datetime import datetime
from PIL import Image
import os.path
import subprocess
import enig_frames.services.base_media_service


class OfficeService(enig_frames.services.base_media_service.BaseMediaService):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(

                     enig_frames.config.Configuration
                 )):
        enig_frames.services.base_media_service.BaseMediaService.__init__(
            self,__name__, configuration
        )
        self.output_dir = os.path.join(self.processing_folder,"out_put")
        self.user_profile_dir= os.path.join(self.processing_folder,"temp_profile")
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir,exist_ok = True)
        if not os.path.isdir(self.user_profile_dir):
            os.makedirs(self.user_profile_dir,exist_ok = True)
        if not os.path.isfile(self.configuration.config.libre_office_path):
            raise Exception(f"Sorry that {self.configuration.config.libre_office_path} not found")

    def convert_to_image(self,office_file_path:str):
        uno = f"Negotiate=0,ForceSynchronous=1;"

        user_profile_id = str(uuid.uuid4())  # Tạo user profile giả, nếu kg có điều này LibreOffice chỉ tạo 1 instance,
        # kg xử lý song song được
        full_user_profile_path = os.path.join(self.user_profile_dir, user_profile_id)
        pid = subprocess.Popen(
            [
                self.configuration.config.libre_office_path,
                '--headless',
                '--convert-to', 'png',
                f"--accept={uno}",
                f"-env:UserInstallation=file://{full_user_profile_path.replace(os.sep, '/')}",
                '--outdir',
                self.output_dir, office_file_path
            ],
            shell=False
        )
        ret = pid.communicate()  # Đợi
        filename_only = pathlib.Path(office_file_path).stem
        shutil.rmtree(full_user_profile_path)
        ret_file = os.path.join(self.output_dir, f"{filename_only}.png")
        return ret_file
