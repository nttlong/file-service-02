import enig_frames.containers

import fasty
from fastapi import Request, Depends, Body, Response
import fasty.JWT
import fasty.JWT_Docs
import api_models.documents as Docs
from ReCompact.db_async import get_db_context
import api_models.documents as Docs
import ReCompact.es_search as search_engine
from typing import Optional





@fasty.api_post("/{app_name}/search")
async def file_search(request: Request, app_name: str, content: str = Body(embed=True),
                      page_size: Optional[int] = Body(embed=True), page_index: Optional[int] = Body(embed=True),
                      highlight: Optional[bool] =Body(None,embed=True),
                      token: str = Depends(fasty.JWT.oauth2_scheme)):
    """
    Tim kiem noi dung
    :param request:
    :param app_name:
    :param content:
    :param page_size:
    :param page_index:
    :param token:
    :return:
    """
    if highlight is None:
        highlight=False
    container = enig_frames.containers.Container
    db_name = container.db_context.get_db_name(app_name)
    if db_name is None:
        return Response(status_code=403)
    # search_result = search_content_of_file(app_name, content, page_size, page_index)
    search_result=container.Services.search_engine.do_full_text_search(
        app_name=app_name,
        content =content,
        page_size=page_size,
        page_index=page_index,
        highlight=highlight
    )

    ret_items = []
    url = container.Services.host.root_api_url
    for x in search_result["items"]:
        upload_doc_item = x.get('data_item')
        if upload_doc_item:
            upload_doc_item['UploadId'] = upload_doc_item["_id"]
            upload_doc_item['Highlight'] = x.get('highlight', [])
            upload_doc_item[
                "UrlOfServerPath"] = url + f"/{app_name}/file/{upload_doc_item[Docs.Files.FullFileName.__name__]}"
            upload_doc_item["AppName"] = app_name
            upload_doc_item[
                "RelUrlOfServerPath"] = f"/{app_name}/file/{upload_doc_item[Docs.Files.FullFileName.__name__]}"
            upload_doc_item[
                "ThumbUrl"] = url + f"/{app_name}/thumb/{upload_doc_item['_id']}/{upload_doc_item[Docs.Files.FileName.__name__]}.png"
            ret_items += [upload_doc_item]

    return dict(
        total_items=search_result["total_items"],
        max_score=search_result["max_score"],
        items=ret_items,
        text_search=search_result["text_search"]
    )
