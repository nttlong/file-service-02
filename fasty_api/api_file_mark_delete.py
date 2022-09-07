import bson

import fasty
from fastapi import Body, Depends, Response
from api_models.documents import Files
from ReCompact.db_async import get_db_context
from fasty.JWT import get_db_name_async, get_oauth2_scheme
import ReCompact.es_search as search_engine

@fasty.api_post("/{app_name}/files/mark_delete")
async def mark_delete(app_name: str, UploadId: str = Body(embed=True),IsDelete:bool=Body(embed=True), token: str = Depends(get_oauth2_scheme())):
    """
    Danh dau xoa
    :param app_name:
    :param UploadId:
    :param IsDelete: True if mark deleted False if not
    :param token:
    :return:
    """

    # 2123d6ba-7c77-4a98-b4b7-7d45c8bc97ab
    db_name = await  get_db_name_async(app_name)
    if db_name is None:
        return Response(status_code=403)
    db_context = get_db_context(db_name)
    delete_item = await db_context.find_one_async(Files, Files._id == UploadId)
    gfs = db_context.get_grid_fs()
    main_file_id = delete_item.get(Files.MainFileId.__name__)

    ret = await db_context.update_one_async(Files, Files._id == UploadId,
        Files.MarkDelete==IsDelete
    )
    bool_body = {
        "bool": {
            "must":
                {"match": {
                    "path.virtual": f'/{app_name}/{delete_item.get(Files._id.__name__)}.{delete_item.get(Files.FileExt.__name__)}'}}
        }
    }
    resp = search_engine.get_client().search(index=fasty.config.search.index, query=bool_body)
    if resp.body.get('hits') and resp.body['hits']['hits'] and resp.body['hits']['hits'].__len__() > 0:
        es_id = resp.body['hits']['hits'][0]['_id']
        body = resp.body['hits']['hits'][0].get('_source')
        body['MarkDelete']=mark_delete
        search_engine.get_client().update(
            index=fasty.config.search.index,
            id=es_id,
            body={"doc": {
                "MarkDelete": IsDelete
            }})
        # search_engine.get_client().delete(index=fasty.config.search.index, id=es_id)
    return dict()