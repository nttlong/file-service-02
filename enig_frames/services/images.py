import pathlib
from PIL import Image
import enig
import enig_frames.config
import os
import enig_frames.services.base_media_service
import enig_frames.services.file_system_utils
import enig_frames.loggers
import img2pdf
import ocrmypdf


class ImageServices(enig_frames.services.base_media_service.BaseMediaService):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(
                     enig_frames.config.Configuration
                 ),
                 file_system_utils: enig_frames.services.file_system_utils.FileSystemUtils = enig.depen(
                     enig_frames.services.file_system_utils.FileSystemUtils
                 ),
                 loggers: enig_frames.loggers.Loggers = enig.depen(
                     enig_frames.loggers.Loggers
                 )):
        enig_frames.services.base_media_service.BaseMediaService.__init__(
            self,
            __name__,
            configuration
        )
        self.logger = loggers.get_logger(__name__)
        self.file_system_utils: enig_frames.services.file_system_utils.FileSystemUtils = file_system_utils
        self.convert_folder = os.path.join(self.processing_folder, "pdf_convert")
        if not os.path.isdir(self.convert_folder):
            os.makedirs(self.convert_folder, exist_ok=True)

    def create_thumbs(self, image_file_path, size: int = 350):
        try:
            filename_only = self.file_system_utils.get_file_name_only(image_file_path)

            # thumb_dir = os.path.join(temp_thumb, app_name)
            image = Image.open(image_file_path)
            h, w = image.size
            thumb_width, thumb_height = size, size
            rate = float(thumb_width / w)
            if h > w:
                rate = float(thumb_height / h)
            nh, nw = rate * h, rate * w
            image.thumbnail((nh, nw))
            thumb_file_path = os.path.join(self.processing_folder, f"{filename_only}_{size}.webp")
            image.save(thumb_file_path)
            image.close()
            del image
            return thumb_file_path
        except Exception as e:
            self.logger.exception(e)

    def convert_to_pdf(self, image_file_path: str):
        image = Image.open(image_file_path)
        file_name = self.file_system_utils.get_file_name_only(image_file_path)
        ret = os.path.join(self.convert_folder, f"{file_name}.pdf")
        pdf_bytes = img2pdf.convert(image.filename)
        file = open(ret, "wb")
        file.write(pdf_bytes)
        image.close()
        file.close()
        return ret
