import os
import pathlib

import enig
import enig_frames.config
from moviepy.editor import *
from matplotlib import pyplot as plt
from PIL import Image
import io
import enig_frames.services.base_media_service


class VideoInfo:
    def __init__(self):
        self.duration = None
        self.fps = None
        self.width = None
        self.height = None


class VideoService(enig_frames.services.base_media_service.BaseMediaService):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(

                     enig_frames.config.Configuration
                 )):
        enig_frames.services.base_media_service.BaseMediaService.__init__(
            self, __name__, configuration
        )

    def get_image_from_frame(self, file_path: str) -> str:
        clip = VideoFileClip(
            file_path
        )
        second, _ = divmod(clip.duration, 2)
        clip = clip.subclip(second, second)
        frame = clip.get_frame(0)
        height, width, _ = frame.shape

        img = Image.fromarray(frame, 'RGB')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        # bytes_of_image = io.BytesIO(img_byte_arr)

        image_file_name_only = pathlib.Path(file_path).stem

        ret_file = os.path.join(self.processing_folder, f"{image_file_name_only}.png")
        with open(ret_file, 'wb') as f:  ## Excel File
            f.write(img_byte_arr)
        del img_byte_arr
        img.close()
        clip.close()
        del img
        del clip
        return ret_file

    def get_info(self, file_path) -> VideoInfo:
        if not os.path.isfile(file_path):
            return None
        clip = VideoFileClip(
            file_path
        )
        ret = VideoInfo()
        ret.duration = clip.duration
        ret.fps = clip.fps
        ret.width = clip.size[0]
        ret.height = clip.size[1]
        clip.close()
        del clip
        return ret
