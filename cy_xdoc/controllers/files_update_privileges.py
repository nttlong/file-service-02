import fastapi
import typing

import cy_docs
import cy_kit
import cy_web
import cy_xdoc.auths
import cy_xdoc.models.files
import cy_xdoc.controllers.models.files_register
import cy_xdoc.services.files
@cy_web.model()
class DataPrivileges:
    UploadId:str
    Privileges: typing.List[cy_xdoc.controllers.models.files_register.PrivilegesType]
@cy_web.hanlder(method="post",path="{app_name}/files/update_privileges")
def update_privileges(
        app_name:str,

        Data : typing.List[cy_xdoc.controllers.models.files_register.PrivilegesType],
        UploadId:str,
        token = fastapi.Depends(cy_xdoc.auths.Authenticate)):
    file_servics = cy_kit.singleton(cy_xdoc.services.files.FileServices)
    ret=file_servics.update_privileges(
        app_name=app_name,
        upload_id=UploadId,
        privileges=[cy_docs.DocumentObject(x) for x in Data]

    )
    return ret
