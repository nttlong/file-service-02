import bson

import fasty
from fastapi import Body, Depends, Response
from api_models.documents import Files,Fs_File
from ReCompact.db_async import get_db_context
from fasty.JWT import get_db_name_async, get_oauth2_scheme
import ReCompact.es_search as search_engine

@fasty.api_post("/{app_name}/files/delete")
async def files_delete(app_name: str, UploadId: str = Body(embed=True), token: str = Depends(get_oauth2_scheme())):
    db_name = await  get_db_name_async(app_name)
    if db_name is None:
        return Response(status_code=403)
    db_context = get_db_context(db_name)
    delete_item = await db_context.find_one_async(Files, Files._id == UploadId)
    gfs = db_context.get_grid_fs()
    at = delete_item.get(Files.AvailableThumbs.__name__,[])
    for x in at:
        d_fs = await  db_context.find_one_async(

            Fs_File,
            Fs_File.rel_file_path ==x
        )
        if d_fs is not None:
            gfs.delete(bson.ObjectId(d_fs.get("_id")))

    main_file_id = delete_item.get(Files.MainFileId.__name__)
    if main_file_id:
        gfs.delete(bson.ObjectId(main_file_id))
    thumb_file_id = delete_item.get(Files.ThumbFileId.__name__)
    if thumb_file_id:
        gfs.delete(bson.ObjectId(thumb_file_id))

    ret = await db_context.delete_one_async(Files, Files._id == UploadId)
    bool_body = {
        "bool": {
            "must":
                {"match":{"path.virtual": f'/{app_name}/{delete_item.get(Files._id.__name__)}.{delete_item.get(Files.FileExt.__name__)}'}}
        }
    }
    resp = search_engine.get_client().search(index=fasty.config.search_engine.index, query=bool_body)
    if resp.body.get('hits') and resp.body['hits']['hits'] and resp.body['hits']['hits'].__len__()>0:
        es_id = resp.body['hits']['hits'][0]['_id']
        search_engine.get_client().delete(index= fasty.config.search_engine.index, id= es_id)
    return dict()
