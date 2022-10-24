import time
from builtins import set

from matplotlib import pyplot as plt

import enig_frames.services.base_media_service
import enig
import glob, fitz
import os
import enig_frames.services.file_system_utils
import subprocess


class ExeFileService(enig_frames.services.base_media_service.BaseMediaService):
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
        import pathlib
        self.ext_lib_folder = os.path.join(str(pathlib.Path(__file__).parent), "ext_libs")
        self.file_system_utils: enig_frames.services.file_system_utils.FileSystemUtils = file_system_utils
        self.output_dir = os.path.join(self.processing_folder, "out_put")
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)

    def extract_icon(self, exe_file: str):
        import pathlib

        filename_only = pathlib.Path(exe_file).stem

        ret_file = os.path.join(self.output_dir, f"{filename_only}.ico")
        # icoextract [-h] [-V] [-n NUM] [-v] input output
        # print(f"{exec_path} {exe_file} {ret_file}")
        # exec_path = os.path.join(self.ext_lib_folder,"icoextract")
        # import icoextract
        # import argparse
        # import logging

        from icoextract import IconExtractor, logger, __version__

        def run(input: str, ouput: str):
            extractor = IconExtractor(input)
            extractor.export_icon(ouput, num=0)
            return ouput

        return run(exe_file, ret_file)
