import fastapi
import cy_kit
from cy_xdoc.services.apps import AppServices
from cy_xdoc.services.accounts import AccountService
from cy_xdoc.services.files import FileServices
@cy_kit.container()
class libs:
    class Services:
        app = cy_kit.single(AppServices)
        account = cy_kit.single(AccountService)
class Container:
    def __call__(self, request: fastapi.Request):
        return libs
def container() -> libs:
    return fastapi.Depends(Container())
def inject() -> libs:
    return fastapi.Depends(Container())
class all:
    class services:
        files:FileServices=cy_kit.single(FileServices)
