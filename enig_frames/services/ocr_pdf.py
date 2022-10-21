import os
import pathlib

import enig
import enig_frames.config
from moviepy.editor import *
from matplotlib import pyplot as plt
from PIL import Image
import io
import uuid
import shutil
from datetime import datetime
from PIL import Image
import os.path
import subprocess
import enig_frames.services.base_media_service
import pdfplumber
import ocrmypdf
import enig_frames.services.file_system_utils


class OcrPdfService(enig_frames.services.base_media_service.BaseMediaService):
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
        self.output_dir = os.path.join(self.processing_folder, "ocr")
        self.user_profile_dir = os.path.join(self.processing_folder, "temp_profile")
        if not os.path.isdir(self.output_dir):
            os.makedirs(self.output_dir, exist_ok=True)
        if not os.path.isdir(self.user_profile_dir):
            os.makedirs(self.user_profile_dir, exist_ok=True)
        if not os.path.isfile(self.configuration.config.libre_office_path):
            raise Exception(f"Sorry that {self.configuration.config.libre_office_path} not found")
        self.file_system_utils : enig_frames.services.file_system_utils.FileSystemUtils = file_system_utils

    def detect_is_ocr(self, pdf_file_path: str):
        """
        Check is pdf file ready ORC?
        :param file_path:
        :return:
        """
        if not os.path.isfile(pdf_file_path):
            return True

        with pdfplumber.open(pdf_file_path) as pdf:
            """
            Check have pdf file been ORC?
            """
            if pdf.pages.__len__() == 0:
                """
                Nothing to do
                """
                return True
            for page in pdf.pages:
                text = page.extract_text()
                if text.__len__() > 0:
                    return True
            return False

    def do_ocr_pdf(self, pdf_file: str):

        """
                Thuc hien ocr pdf file trong tien tring rieng biet
                :param file_path:
                :param out_put_file_path:
                :return:
                """
        file_name_only = self.file_system_utils.get_file_name_only(pdf_file)
        out_put_file_path = os.path.join(self.output_dir, f"{file_name_only}.pdf")
        fx = ocrmypdf.ocr(
            input_file=pdf_file,
            output_file=out_put_file_path,
            progress_bar=False,
            language="vie+eng",
            use_threads=False,
            skip_text=True,
            jobs=100,
            keep_temporary_files=True
        )
        return out_put_file_path
