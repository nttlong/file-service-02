from django.views.decorators.http import require_http_methods
import ReCompact.db_context
import ReCompact.dbm
import api_models.Model_Files
import ReCompact.HttpStream
from django.http.response import HttpResponse
@require_http_methods(["GET"])
def source(request,app_name,upload_id):
    db = ReCompact.db_context.get_db(app_name)
    upload_item = ReCompact.dbm.DbObjects.find_to_object(
        db,
        data_item_type= api_models.Model_Files.DocUploadRegister,
        filter= ReCompact.dbm.FILTER._id ==upload_id
    )
    if upload_item and upload_item.ThumbFileId:
        fs =ReCompact.db_context.get_mongodb_file_by_file_id(db,upload_item.ThumbFileId)
        if fs:
            return ReCompact.HttpStream.streaming_mongo_db_fs(request, fs)


    return HttpResponse(status=204)