from cyx.common.base import config


class LibreOfficeService:
    def __init__(self):
        self.config = config
        self.libre_office_path = self.config.libre_office_path

    def get_image(self, file_path)->str:
        raise NotImplemented
