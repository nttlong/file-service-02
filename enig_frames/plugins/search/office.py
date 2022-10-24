import os

import enig
import enig_frames.plugins.base_plugin
import enig_frames.config
import api_models.documents
import enig_frames.services.file_system_utils
import enig_frames.services.PDFs
import enig_frames.services.file_system
import enig_frames.services.files
import enig_frames.services.office
import enig_frames.services.search_engine

class Office(enig_frames.plugins.base_plugin.BasePlugin):
    def __init__(
            self,
            configuration: enig_frames.config.Configuration = enig.depen(
                enig_frames.config.Configuration
            ),
            file_system_utils: enig_frames.services.file_system_utils = enig.depen(
                enig_frames.services.file_system_utils.FileSystemUtils
            ),

            file_system_services: enig_frames.services.file_system.FileSystem = enig.depen(
                enig_frames.services.file_system.FileSystem
            ),
            file_services: enig_frames.services.files.Files = enig.depen(
                enig_frames.services.files.Files
            ),
            search_engine: enig_frames.services.search_engine.SearchEngineService = enig.depen(
                enig_frames.services.search_engine.SearchEngineService
            )
    ):
        self.configuration: enig_frames.config.Configuration = configuration
        self.file_system_utils: enig_frames.services.file_system_utils.FileSystemUtils = file_system_utils
        # self.pdf_file_service: enig_frames.services.PDFs.PdfFileService = pdf_file_service
        self.file_system_services:enig_frames.services.file_system.FileSystem = file_system_services
        self.file_services:enig_frames.services.files.Files= file_services
        self.search_engine:enig_frames.services.search_engine.SearchEngineService = search_engine

        enig_frames.plugins.base_plugin.BasePlugin.__init__(self)

    def process(self, file_path: str, app_name: str, upload_id: str):
        mime_type = self.file_system_utils.get_mime_type(file_path)
        file_ext = self.file_system_utils.get_file_extenstion(file_path)
        # if '-officedocument.' in mime_type \
        #         or file_ext.lower() in self.configuration.config.ext_office_file \
        #         or file_ext.upper() in self.configuration.config.ext_office_file:
        if file_ext.lower()!="pdf" and not mime_type.lower().startswith('image/'):
            file_ext_only = self.file_system_utils.get_file_extenstion(file_path)
            file_name_only = self.file_system_utils.get_file_name_only(file_path)
            self.search_engine.make_index_content(
                app_name=app_name,
                file_path=file_path,
                upload_id=upload_id,
                data_item= self.file_services.get_item_by_upload_id(
                    app_name=app_name,
                    upload_id=upload_id
                )
            )




