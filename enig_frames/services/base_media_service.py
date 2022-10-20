import enig
import pathlib
import os
import enig_frames.config


class BaseMediaService(enig.Singleton):
    def __init__(self,name:str, configuration: enig_frames.config.Configuration):
        self.configuration: enig_frames.config.Configuration = configuration
        self.working_folder = str(pathlib.Path(__file__).parent.parent.parent)
        self.processing_folder = self.configuration.config.tmp_media_processing_folder
        if self.processing_folder[0:2] == "./":
            self.processing_folder = self.processing_folder[2:]
            self.processing_folder = os.path.join(self.working_folder, self.processing_folder)
        self.processing_folder = os.path.join(self.processing_folder, name)
        self.processing_folder = self.processing_folder.replace('/', os.sep)
        if not os.path.isdir(self.processing_folder):
            os.makedirs(self.processing_folder)

    def get_file_extenstion(self, file_path) -> str:
        ret = os.path.splitext(file_path)[1]
        return ret[1:]

    def get_file_name_only(self, file_path):
        return pathlib.Path(file_path).stem
