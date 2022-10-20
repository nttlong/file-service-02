from builtins import set

from matplotlib import pyplot as plt

import enig_frames.services.base_media_service
import enig
import glob, fitz
import os
import enig_frames.services.file_system_utils
class PdfFileService(enig_frames.services.base_media_service.BaseMediaService):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(

                     enig_frames.config.Configuration
                 ),
                 file_system_utils: enig_frames.services.file_system_utils.FileSystemUtils = enig.depen(
                     enig_frames.services.file_system_utils.FileSystemUtils
                 )):
        enig_frames.services.base_media_service.BaseMediaService.__init__(
            self, __name__, configuration
        )
        self.file_system_utils:enig_frames.services.file_system_utils.FileSystemUtils = file_system_utils

    def convert_to_image(self, pdf_file: str):
        filename_only = self.file_system_utils.get_file_name_only(pdf_file)
        image_file_path = os.path.join(self.processing_folder, f"{filename_only}.png")
        if os.path.isfile(image_file_path):
            return image_file_path
        # To get better resolution
        zoom_x = 2.0  # horizontal zoom
        zoom_y = 2.0  # vertical zoom
        mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

        all_files = glob.glob(pdf_file)



        for filename in all_files:
            doc = fitz.open(filename)  # open document
            for page in doc:  # iterate through the pages
                pix = page.get_pixmap()  # render page to an image
                pix.save(image_file_path)  # store image as a PNG
                break  # Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
            break  # Hết vòng lặp luôn Chỉ xử lý trang đầu, bất chấp có nôi dung hay không?
        return image_file_path