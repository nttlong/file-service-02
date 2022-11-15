import cy_web
from fastapi import Request,Depends,status
from cy_xdoc import inject
from fastapi_jwt_auth import AuthJWT
from fastapi.responses import RedirectResponse
@cy_web.hanlder(method="get",path="sso/signin/{SSOID}")
async def do_sign_in(SSOID: str, request: Request,injector=inject()):
    """
    Đăng nhập vào dịch vụ bằng SSOID.
    Khi 1 web site remote muốn truy cập vào dịch vụ bằng trình duyệt,
    nhưng lại không thể gởi access token qua header hoặc request params.
    (Ví dụ như xem nôi dung file bằng url của dịch vụ ngay tại site remote)
    Thì web site remote phải redirect sang url của dịch vụ để có thể truy cập được

    :param app_name:
    :param SSOID:
    :param request:
    :param Authorize:
    :return:
    """
    # accounts_services= enig.depen(enig_frames.services.accounts.Accounts)
    sso_info = injector.Services.account.get_sso_login(

        id=SSOID
    ) # await container.Services.accounts.get_sso_login_asycn(SSOID=SSOID)

    ret_url = sso_info.ReturnUrlAfterSignIn
    if ret_url is None:
        return cy_web.get_host_url()

    ret_url = request.query_params.get('ret', ret_url)

    res = RedirectResponse(url=ret_url, status_code=status.HTTP_303_SEE_OTHER)
    res.set_cookie("access_token_cookie", sso_info.Token)
    return res