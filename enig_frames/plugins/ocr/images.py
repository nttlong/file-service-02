import os

import enig
import enig_frames.plugins.base_plugin
import enig_frames.config
import api_models.documents
import enig_frames.services.file_system_utils
import enig_frames.services.PDFs
import enig_frames.services.images
import enig_frames.services.file_system
import enig_frames.services.files
import enig_frames.services.ocr_pdf

class Images(enig_frames.plugins.base_plugin.BasePlugin):
    def __init__(
            self,
            configuration: enig_frames.config.Configuration = enig.depen(
                enig_frames.config.Configuration
            ),
            file_system_utils: enig_frames.services.file_system_utils = enig.depen(
                enig_frames.services.file_system_utils.FileSystemUtils
            ),
            pdf_file_service: enig_frames.services.PDFs.PdfFileService = enig.depen(
                enig_frames.services.PDFs.PdfFileService
            ),
            image_service: enig_frames.services.images.ImageServices = enig.depen(
                enig_frames.services.images.ImageServices
            ),
            file_system_services: enig_frames.services.file_system.FileSystem = enig.depen(
                enig_frames.services.file_system.FileSystem
            ),
            file_services: enig_frames.services.files.Files = enig.depen(
                enig_frames.services.files.Files
            ),
            ocr_pdf_services: enig_frames.services.ocr_pdf.OcrPdfService = enig.depen(
                enig_frames.services.ocr_pdf.OcrPdfService
            )
    ):
        self.configuration: enig_frames.config.Configuration = configuration
        self.file_system_utils: enig_frames.services.file_system_utils.FileSystemUtils = file_system_utils
        self.pdf_file_service: enig_frames.services.PDFs.PdfFileService = pdf_file_service
        self.image_service: enig_frames.services.images.ImageServices = image_service
        self.file_system_services: enig_frames.services.file_system.FileSystem = file_system_services
        self.file_services: enig_frames.services.files.Files = file_services
        self.ocr_pdf_services: enig_frames.services.ocr_pdf.OcrPdfService = ocr_pdf_services
        enig_frames.plugins.base_plugin.BasePlugin.__init__(self)

    def process(self, file_path: str, app_name: str, upload_id: str):
        mime_type = self.file_system_utils.get_mime_type(file_path)
        if mime_type.lower().startswith("image/"):
            file_ext_only = self.file_system_utils.get_file_extenstion(file_path)
            file_name_only = self.file_system_utils.get_file_name_only(file_path)
            pdf_file = self.image_service.convert_to_pdf(file_path)
            if not  os.path.isfile(pdf_file):
                return

            ocr_pdf_file = self.ocr_pdf_services.do_ocr_pdf(pdf_file=pdf_file)
            if not os.path.isfile(ocr_pdf_file):
                os.remove(pdf_file)
                return
            file_info = self.file_system_services.upload(
                app_name=app_name,
                full_path_to_file=ocr_pdf_file

            )
            #file-ocr/99c03943-3ba7-4087-96e6-088221d74804/Nguyen_Ky_chinh.pdf
            rel_file_path = f"file-ocr/{upload_id}/{file_name_only}.pdf"
            self.file_services.update_rel_path(
                app_name=app_name,
                file_id=str(file_info._id),
                rel_file_path=rel_file_path)
            self.file_services.update_file_field(
                app_name=app_name,
                upload_id=upload_id,
                field=api_models.documents.Files.OCRFileId,
                value=file_info._id

            )


