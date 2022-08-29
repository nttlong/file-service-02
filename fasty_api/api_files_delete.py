import bson

import fasty
from fastapi import Body, Depends, Response
from api_models.documents import Files
from ReCompact.db_async import get_db_context
from fasty.JWT import get_db_name_async, get_oauth2_scheme


@fasty.api_post("/{app_name}/files/delete")
async def files_upload(app_name: str, UploadId: str = Body(embed=True), token: str = Depends(get_oauth2_scheme())):
    db_name = await  get_db_name_async(app_name)
    if db_name is None:
        return Response(status_code=403)
    db_context = get_db_context(db_name)
    delete_item = await db_context.find_one_async(Files, Files._id == UploadId)
    gfs = db_context.get_grid_fs()
    main_file_id = delete_item.get(Files.MainFileId.__name__)
    if main_file_id:
        gfs.delete(bson.ObjectId(main_file_id))
    thumb_file_id = delete_item.get(Files.ThumbFileId.__name__)
    if thumb_file_id:
        gfs.delete(bson.ObjectId(thumb_file_id))

    ret = await db_context.delete_one_async(Files, Files._id == UploadId)
    return dict()
