# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
import ReCompact.db_context
import api_models.Model_Files
import ReCompact.api_input
from django.http import JsonResponse,HttpResponse

class Filter:
    PageSize= (int,False)
    PageIndex = (int,False)
    FieldSearch =(str,False)
    ValueSearch =(str,False)


@ReCompact.api_input.map_param(cls_params=Filter)
@require_http_methods(["POST"])
def get_list(request,app_name,data:Filter,error:ReCompact.api_input.Error):

    if error:
        return error.to_error_500()

    if data is None:
        data= Filter()
        data.PageIndex=0
        data.PageSize=50
    if data.PageSize is None:
        data.PageSize=50
    if data.PageIndex is None:
        data.PageIndex=0
    import ReCompact.db_context
    import mimetypes
    import ReCompact.dbm
    import re

    db = ReCompact.db_context.get_db(app_name)


    agg = ReCompact.dbm.DbObjects.aggregrate(db, api_models.Model_Files.DocUploadRegister)
    if data.ValueSearch and data.ValueSearch!="" and data.FieldSearch=="FileName":
        agg = agg.match(
            ReCompact.dbm.FILTER.FileName==re.compile(data.ValueSearch,re.IGNORECASE)
        )
    agg = agg.sort(
        ReCompact.dbm.DbObjects.FIELDS.RegisterOn.desc(),
        ReCompact.dbm.DbObjects.FIELDS.FileName.asc()
    ).skip(data.PageSize*data.PageIndex).limit(data.PageSize)
    ret_list = list(agg)
    ret=[]
    for x in ret_list:
        ThumbUrl = None
        if x.get("HasThumb",None) is None:
            x["HasThumb"]=False
            if x.get("ThumbFileId",None) is not None:
                x["HasThumb"] = True
                ReCompact.dbm.DbObjects.update(
                    db,
                    data_item_type= api_models.Model_Files.DocUploadRegister,
                    filter= ReCompact.dbm.DbObjects.FILTER._id == x["_id"],
                    updator= ReCompact.dbm.SET(
                        ReCompact.dbm.FIELDS.HasThumb==x["HasThumb"]
                    )


                )
        if x.get("HasThumb", False):
            ThumbUrl = f"{request._current_scheme_host}/api/files/{app_name}/thumb/{x.get('_id',None)}.png"
        if x.get("MimeType",None) is None:
            ReCompact.dbm.DbObjects.update(
                db,
                api_models.Model_Files.DocUploadRegister,
                ReCompact.dbm.DbObjects.FILTER.FileName==x["FileName"],
                ReCompact.dbm.SET(
                    ReCompact.dbm.DbObjects.FIELDS.MimeType==mimetypes.guess_type(x["FileName"])[0]
                )
            )
        full_name = str(x.get('FileName',""))
        if full_name.endswith("_thumb.png"):
            thumb_info = ReCompact.dbm.DbObjects.find_to_object(
                db,
                data_item_type= api_models.Model_Files.DocUploadRegister,
                filter= ReCompact.dbm.FILTER.FileName==full_name
            )
            if thumb_info:
                fs = ReCompact.db_context.get_mongodb_file_by_file_name(
                    db,
                    thumb_info.ServerFileName
                )
                if fs:
                    ReCompact.dbm.DbObjects.update(
                        db,
                        data_item_type= api_models.Model_Files.DocUploadRegister,
                        filter= ReCompact.dbm.FIELDS.ThumbId==thumb_info._id,
                        updator= ReCompact.dbm.SET(
                            ReCompact.dbm.FIELDS.ThumbFileId == fs._id
                        )
                    )
                    ReCompact.dbm.DbObjects.delete(
                        db,
                        data_item_type= api_models.Model_Files.DocUploadRegister,
                        filter= ReCompact.dbm.FIELDS._id == thumb_info._id
                    )

        else:
            ProcessHistories = x.get("ProcessHistories", None)

            if isinstance(ProcessHistories,list):
                for item in ProcessHistories:
                    item["_id"]=None
            else:
                ProcessHistories =[]
            original_file_id = x.get("OriginalFileId", None)
            url_of_original_source = None
            if original_file_id is not None:
                original_file_id=str(original_file_id)
                url_of_original_source=f"{request._current_scheme_host}/api/files/{app_name}/original/{x.get('FullFileName',None)}"
            OCR_file_id = x.get("OCRFileId",None)
            url_of_ocr_source = None
            if OCR_file_id is not None:
                OCR_file_id=str(OCR_file_id)
                url_of_ocr_source =f"{request._current_scheme_host}/api/files/{app_name}/ocr/{x.get('FullFileName',None)}"
            ret+=[
                dict(
                    Status =x.get("Status",0),
                    FileName=x.get("FileName",None),
                    FileExt =x.get("FileExt",None),
                    MimeType =x.get("MimeType",mimetypes.guess_type(x.get("FileName","a.dat"))[0]),
                    RegisterOn =x.get("RegisterOn",None),
                    SizeInHumanReadable =x.get("SizeInHumanReadable",None),
                    UrlOfServerPath =f"{request._current_scheme_host}/api/files/{app_name}/directory/{x.get('FullFileName',None)}",
                    HasThumb = x.get("HasThumb",False),
                    ThumbUrl =ThumbUrl,
                    # OriginalFileId= x.get("OriginalFileId",None),
                    # OCRFileId =x.get("OCRFileId",None),
                    LastModifiedOn = x.get("LastModifiedOn",None),
                    VideoDuration =x.get("VideoDuration",None),
                    VideoFPS =x.get("VideoFPS",None),
                    VideoResolutionWidth =x.get("VideoResolutionWidth",None),
                    VideoResolutionHeight =x.get("VideoResolutionHeight",None),
                    ProcessHistories=ProcessHistories,
                    UrlOfOriginalSource = url_of_original_source,
                    UrlDfOCRSource =url_of_ocr_source
                )
            ]

    return JsonResponse(ret, safe=False)

