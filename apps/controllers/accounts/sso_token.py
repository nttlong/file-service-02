import cy_web
@cy_web.get("get_sso_token")
def get_sso_token():
    return dict(ok=123)