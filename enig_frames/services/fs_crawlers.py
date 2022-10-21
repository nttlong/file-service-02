import os.path
import pathlib
import shutil

import enig
import enig_frames.config
import enig_frames.services.file_system_utils


class FsCrawler(enig.Singleton):
    def __init__(self,
                 configuration: enig_frames.config.Configuration = enig.depen(
                     enig_frames.config.Configuration
                 ),
                 file_utils: enig_frames.services.file_system_utils.FileSystemUtils = enig.depen(
                     enig_frames.services.file_system_utils.FileSystemUtils
                 )):
        self.configuration: enig_frames.config.Configuration = configuration
        self.fs_crawler_path = self.configuration.config.fs_crawler_path
        self.file_utils: enig_frames.services.file_system_utils.FileSystemUtils = file_utils
        self.working_dir = str(pathlib.Path(__file__).parent.parent)
        if self.fs_crawler_path[0:2] == './':
            self.fs_crawler_path = os.path.join(self.working_dir, self.fs_crawler_path[2:]).replace('/', os.sep)
            if not os.path.isdir(self.fs_crawler_path):
                os.makedirs(self.fs_crawler_path, exist_ok=True)

    def move_to_fs_crawler_directory(self, app_name: str, file_path):
        file_name_only = self.file_utils.get_file_name_only(file_path)
        file_ext_only = self.file_utils.get_file_name_only(file_path)
        full_app_dir = os.path.join(self.fs_crawler_path, app_name)
        if not os.path.isdir(full_app_dir):
            os.makedirs(full_app_dir, exist_ok=True)
        full_dest_path = os.path.join(full_app_dir, f"{file_name_only}.{file_ext_only}")
        shutil.move(file_path, full_dest_path)
        return full_dest_path
