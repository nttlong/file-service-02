import os
import pathlib
import sys
from moviepy.editor import *
from matplotlib import pyplot as plt
from PIL import Image
import io

class VideoServices:
    def __init__(self):
        self.working_folder = pathlib.Path(__file__).parent.parent.parent.__str__()
        self.processing_folder = os.path.join(
            self.working_folder,"tmp","video"
        )
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder,exist_ok=True)

    def get_image(self, file_path, duration=None):
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
        if sys.platform == "linux":
            try:
                import ctypes
                libc = ctypes.CDLL("libc.so.6")
                libc.malloc_trim(0)
            except Exception as e:
                return ret_file
        return ret_file