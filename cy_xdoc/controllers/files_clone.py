import pydantic

import cy_kit
import cy_web, fastapi, cy_xdoc, cy_xdoc.auths

from cy_xdoc.controllers.models.files_clone import CloneFileResult
import cy_xdoc.services.files
@cy_web.hanlder(method= "post", path= "{app_name}/files/clone")
def clone_to_new(app_name:str, UploadId: str, token = fastapi.Depends(cy_xdoc.auths.Authenticate)) -> CloneFileResult:
    ret_copy = CloneFileResult()
    # 2123d6ba-7c77-4a98-b4b7-7d45c8bc97ab
    file_service:cy_xdoc.services.files.FileServices = cy_kit.singleton(cy_xdoc.services.files.FileServices)

    item = file_service.do_copy(app_name=app_name,upload_id=UploadId)
    doc_context = file_service
    if item is None:
        return pydantic.BaseModel(
            Error= pydantic.BaseModel(
                Code="fileNotFound",
                Message="File not found"

            )
        )
    else:
        return  pydantic.BaseModel(
            Info = item
        )










