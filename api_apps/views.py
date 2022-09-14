from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
import ReCompact.dbm.DbObjects
import ReCompact.db_context
import api_models.ModelApps
from django.http import JsonResponse
import ReCompact.auth as rpt_auth
import api_apps.app_params
import ReCompact.api_input


# Create your views here.
@ReCompact.api_input.map_param(api_apps.app_params.AppParam)  # map request body to data view must have data
@require_http_methods(["POST"])

def create_app(request,app_name, data: api_apps.app_params.AppParam, error: ReCompact.api_input.Error):
    """
    Thêm mới hoặc cập nhật thông tin của application
    :param request:
    :param data:
    :param error:
    :return:
    """
    if error: return error.to_json()
    error = ReCompact.api_input.Error()
    import re
    pat = re.compile(r"[A-Za-z][A-Za-z0-9\-_]+")
    if not re.fullmatch(pat, data.Name):
        error.raise_invalid_field("Name")
        return error.to_json()
    if data.Domain.lower() != "localhost":
        regex_domain = "^((?!-)[A-Za-z0-9-]{1,63}(?<!-)\\.)[A-Za-z]{2,6}"
        pat = re.compile(regex_domain)
        if not re.search(pat, data.Domain):
            error.raise_invalid_field("Domain")
            return error.to_json()
    # khai báo regex kiểm tra url có hợp lệ hay không?
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    if not re.match(regex, data.LoginUrl) is not None:
        error.raise_invalid_field("LoginUrl")
        return error.to_json()
    if not re.match(regex, data.ReturnUrlAfterSignIn) is not None:
        error.raise_invalid_field("ReturnUrlAfterSignIn")
        return error.to_json()
    db = ReCompact.db_context.get_db()
    app = ReCompact.dbm.DbObjects.find_to_object(
        db,  # Căn cứ vào database
        api_models.ModelApps.sys_applications,  # Với model
        ReCompact.dbm.FILTER.Name == data.Name  # Tìm app thep tên
    )
    if app is None:
        import uuid
        data_item = api_models.ModelApps.sys_applications(
            _id=str(uuid.uuid4()),
            Name=data.Name,
            Domain=data.Domain,
            LoginUrl=data.LoginUrl,
            ReturnUrlAfterSignIn=data.ReturnUrlAfterSignIn,
            SecretKey = str(uuid.uuid4())

        )
        ReCompact.dbm.DbObjects.insert(
            db,
            data_item

        )
        return data_item.JSON_DATA
    else:
        ReCompact.dbm.DbObjects.update(
            db,
            api_models.ModelApps.sys_applications,
            ReCompact.dbm.FILTER.Name == data.Name,
            ReCompact.dbm.SET(
                ReCompact.dbm.FIELDS.LoginUrl == data.LoginUrl,
                ReCompact.dbm.FIELDS.ReturnUrlAfterSignIn == data.ReturnUrlAfterSignIn
            )
        )
        return data.JSON_DATA


my_post = "POST"


@require_http_methods([my_post])
@rpt_auth.validator()
def list_apps(request, app_name):
    if app_name == 'admin' and request.current_user:
        import ReCompact.db_context
        db = ReCompact.db_context.get_db()

        agg = ReCompact.dbm.DbObjects.aggregrate(db, api_models.ModelApps.sys_applications)
        agg = agg.sort(
            ReCompact.dbm.DbObjects.FIELDS.Name.asc(),
            ReCompact.dbm.DbObjects.FIELDS.Domain.asc(),
        )

        return JsonResponse(list(agg), safe=False)


@require_http_methods(["POST"])
@rpt_auth.validator()
def get_app(request, app_name):
    db_app_name = request.data_body['AppName']
    import ReCompact.db_context
    import ReCompact.dbm
    db = ReCompact.db_context.get_db()
    ret = ReCompact.dbm.DbObjects.find_one_to_dict(
        db,
        api_models.ModelApps.sys_applications,
        ReCompact.dbm.FILTER.Name == db_app_name
    )
    return JsonResponse(ret, safe=False)
