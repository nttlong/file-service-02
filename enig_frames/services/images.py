import pathlib
from PIL import Image
import enig
import enig_frames.config
import os
import enig_frames.services.base_media_service


class ImageServices(enig_frames.services.base_media_service.BaseMediaService):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(
                     enig_frames.config.Configuration
                 )):
        enig_frames.services.base_media_service.BaseMediaService.__init__(
            self,
            __name__,
            configuration
        )

    def create_thumbs(self, image_file_path, size: int = 350):
        filename_only = self.get_file_name_only(image_file_path)

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
