from django.http import HttpResponse
import ReCompact.web
@ReCompact.web.template("index.html")
def index(request):
    if request.session.get('current_user')==None:
        import web.settings
        from django.shortcuts import redirect
        return redirect(web.settings.ROOT_URL+'/'+web.settings.LOGIN_URL)
    return request.template.model({"request":request}).render()
