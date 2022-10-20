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
            os.makedirs(self.processing_folder,exist_ok=True)


