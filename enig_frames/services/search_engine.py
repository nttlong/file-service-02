import gc

import api_models.documents
import enig
import enig_frames.db_context
import enig_frames.repositories.search_engine
import enig_frames.services.sercurities
import enig_frames.config
import enig_frames.db_context
import enig_frames.services.file_content_extractors
import enig_frames.services.file_system_utils
import enig_frames.services.text_processors


class SearchEngineService(enig.Singleton):
    def __init__(self,
                 repo=enig.depen(enig_frames.repositories.search_engine.SearchEngineRepo),
                 configuration=enig.depen(enig_frames.config.Configuration),
                 # db_context=enig.depen(enig_frames.db_context.DbContext),
                 text_extractor_services=enig.depen(
                     enig_frames.services.file_content_extractors.FileContentExtractorService
                 ),
                 file_utils: enig_frames.services.file_system_utils.FileSystemUtils = enig.depen(
                     enig_frames.services.file_system_utils.FileSystemUtils
                 ),
                 text_processor_service: enig_frames.services.text_processors.TextProcessService = enig.depen(
                     enig_frames.services.text_processors.TextProcessService
                 )):
        self.repo: enig_frames.repositories.search_engine.SearchEngineRepo = repo
        self.configuration: enig_frames.config.Configuration = configuration
        self.text_extractor_services: enig_frames.services.file_content_extractors.FileContentExtractorService = text_extractor_services
        self.file_utils: enig_frames.services.file_system_utils.FileSystemUtils = file_utils
        self.text_processor_service: enig_frames.services.text_processors.TextProcessService = text_processor_service

    def make_index_content(self, app_name: str, upload_id: str, file_path: str, data_item: dict):
        content, meta_info = self.text_extractor_services.get_text(file_path)
        index_name = self.get_index_name(app_name)
        file_name = self.file_utils.get_file_name(file_path)
        vn_on_accent_content = self.text_processor_service.vn_clear_accent_mark(content)
        self.repo.create_doc(id=upload_id, index_name=index_name, body=dict(
            app_name=app_name,
            upload_id=upload_id,
            file_name=file_name,
            mark_delete=False,
            content=content,
            vn_on_accent_content=vn_on_accent_content,
            meta_info=meta_info,
            data_item=data_item
        ))
        del content
        del meta_info
        del vn_on_accent_content
        gc.collect()

    def get_index_name(self, app_name) -> str:
        ret = f"{self.configuration.config.elastic_search.prefix_index}_{app_name}"
        self.repo.create_index(ret)
        return f"{self.configuration.config.elastic_search.prefix_index}_{app_name}"

    def remove_doc(self, app_name: str, id: str):
        return self.repo.remove_doc(
            index_name=self.get_index_name(app_name),
            id=id
        )

    def do_full_text_search(self, app_name: str, content: str, page_size: int, page_index: int,highlight:bool):
        return self.repo.do_full_text_search(
            index_name=self.get_index_name(app_name),
            page_size=page_size,
            page_index=page_index,
            content=content,
            highlight=highlight
        )

    def mark_delete(self, app_name: str, id: str, mark_delete_value: bool):
        ret = self.repo.mark_delete(
            index_name=self.get_index_name(app_name),
            mark_delete_value=mark_delete_value,
            id=id
        )
        return ret

    def update_upload_register(self, app_name, id, upload_register):
        ret = self.repo.update_upload_register(
            index_name=self.get_index_name(app_name),
            upload_register=upload_register,
            id=id
        )
        return ret
