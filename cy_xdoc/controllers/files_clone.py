import cy_web, fastapi, cy_xdoc, cy_xdoc.auths

from cy_xdoc.controllers.models.files_clone import CloneFileResult
@cy_web.hanlder(method= "post", path= "{app_name}/files/clone")
def clone_to_new(app_name:str, UploadId: str, token = fastapi.Depends(cy_xdoc.auths.Authenticate)) -> CloneFileResult:
    pass