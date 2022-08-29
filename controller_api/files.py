from flask_restful import Resource

import api_models.Model_Files
import api_models.ModelApps
import re
from  . import base_api

from flask import request

import quicky
import manager.files_manager

@quicky.safe_logger()
class Files(base_api.BaseApi):
    """
    Controller lấy danh sách các file
    """
    def post(self, app_name):
        app_config = quicky.get_app().app_config
        json_data = request.get_json(force=True)
        page_index = json_data.get("PageIndex", 0)
        page_size = json_data.get("PageSize", 20)
        field_search = json_data.get("FieldSearch", None)
        value_search = json_data.get("ValueSearch", None)
        files = api_models.Model_Files.DocUploadRegister(self.connection, app_name)
        if field_search is not None and value_search is not None:
            files.filter(
                getattr(files, field_search) == re.compile(value_search)
            )
        files.skip(page_index * page_size)
        files.limit(page_size)
        ret = list(files)
        for x in ret:
            x["UrlOfServerPath"] = f"{app_config.api_url}/files/{app_name}/directory/{x['FullFileName']}"
            if x.get(files.ThumbFileId.__name__, None) is not None:
                if x.get(files.HasThumb.__name__, None) is None:
                    files.update_one(
                        files._id == x["_id"],
                        files.set(
                            files.HasThumb == True
                        )
                    )
                x["ThumbUrl"] = f"{app_config.api_url}/files/{app_name}/thumb/{x[files._id.__name__]}.png"

        return ret
@quicky.safe_logger()
class FilesFullTextSearch(base_api.BaseApi):
    def post(self,app_name):
        app_config = quicky.get_app().app_config
        data = request.get_json(force=True)
        content = data.get('content','')
        ret = manager.files_manager.search_content_of_file_and_map_upload(app_name,content)
        items =[]
        for x in ret["items"]:
            doc_item = x["doc_item"]
            search_item = x["search_item"]
            ThumbUrl=None
            if doc_item.get("ThumbFileId", None) is not None:
                ThumbUrl = f"{app_config.api_url}/files/{app_name}/thumb/{doc_item['_id']}.png"

            UrlOfServerPath = f"{app_config.api_url}/files/{app_name}/directory/{doc_item['FullFileName']}"
            item = dict(
                UploadId= x["doc_item"]["_id"],
                FileName = x["doc_item"]["FileName"],
                UrlOfServerPath=UrlOfServerPath,
                ThumbUrl=ThumbUrl,
                HasThumb = ThumbUrl is not None,
                IsPublic =doc_item.get('IsPublic',False),
                Highlight = search_item["highlight"],
                Content = search_item["content"],
                SizeInHumanReadable= doc_item.get('SizeInHumanReadable',None),
                Status =doc_item.get('Status',False),
                RegisterOn = doc_item.get('RegisterOn')
            )
            items+=[item]
        ret["items"] = items
        return ret


quicky.api_add_resource(Files, '/files/<app_name>/list')
quicky.api_add_resource(FilesFullTextSearch, '/files/<app_name>/content/search')