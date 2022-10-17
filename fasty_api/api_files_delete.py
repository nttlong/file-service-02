import bson

import enig_frames.containers
import fasty
from fastapi import Body, Depends, Response
from api_models.documents import Files,Fs_File
from ReCompact.db_async import get_db_context
from fasty.JWT import get_db_name_async, get_oauth2_scheme
import ReCompact.es_search as search_engine

@fasty.api_post("/{app_name}/files/delete")
async def files_delete(app_name: str, UploadId: str = Body(embed=True), token: str = Depends(get_oauth2_scheme())):
    container = enig_frames.containers.Container
    db_name = container.db_context.get_db_name(app_name)
    if db_name is None:
        return Response(status_code=403)
    delete_item = await container.Services.files.get_item_by_upload_id_async(app_name, UploadId)
    if delete_item is None:
        return Response(status_code=404)

    # db_context = get_db_context(db_name)
    # delete_item = await db_context.find_one_async(Files, Files._id == UploadId)
    # gfs = db_context.get_grid_fs()
    at = delete_item.get(Files.AvailableThumbs.__name__,[])
    for x in at:
        await container.Services.file_system.delete_by_rel_path_asycn(
            app_name=app_name,
            rel_path =x

        )

    main_file_id = delete_item.get(Files.MainFileId.__name__)
    if main_file_id:
        await container.Services.file_system.delete_by_id_async(app_name,main_file_id)
    thumb_file_id = delete_item.get(Files.ThumbFileId.__name__)
    if thumb_file_id:
        await container.Services.file_system.delete_by_id_async(app_name, thumb_file_id)

    ret = await container.Services.files.delete_by_id_async(app_name,upload_id=UploadId)
    bool_body = {
        "bool": {
            "must":
                {"match":{"path.virtual": f'/{app_name}/{delete_item.get(Files._id.__name__)}.{delete_item.get(Files.FileExt.__name__)}'}}
        }
    }
    resp = container.Services.search_engine.search(
        index=container.config.config.elastic_search.index,
        query=bool_body
    )
    if resp.body.get('hits') and resp.body['hits']['hits'] and resp.body['hits']['hits'].__len__()>0:
        es_id = resp.body['hits']['hits'][0]['_id']
        container.Services.search_engine.delete_by_id(
            index=container.config.config.elastic_search.index,
            id=es_id
        )

    return dict()
