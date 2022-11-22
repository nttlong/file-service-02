from django.http import HttpResponse
from django.shortcuts import redirect
import ReCompact.web
@ReCompact.web.template("login.html")
def do_login(request):
    error= dict()
    from django.contrib.auth.models import User
    from django.contrib.auth import authenticate, login
    from django.shortcuts import redirect

    root_user = User.objects.filter(username='root')
    if not root_user.exists():
        User.objects.create_superuser(
            username='root',
            password='root'

        )
    if request.method=='POST':
        username = None
        passwword = None
        request_body= request.body.decode('utf-8')
        items =request_body.split('&')
        for x in items:
            assert isinstance(x,str)
            if x.startswith('username='):
                username =x.split('=')[1]
            if x.startswith('username='):
                passwword =x.split('=')[1]
        user = authenticate(username=username, password=passwword)
        if user==None:
            error["messag"]="login_fail"
        else:
            request.session['current_user'] = dict(
                username=user.username
            )

            if request.GET.get("ret") is None:
                return redirect(
                    to='/'
                )
            else:
                return redirect(
                    to=request.GET.get("ret")
                )

    return request.template.model({"request": request}).render()

from django.http import HttpResponse
import ReCompact.web
@ReCompact.web.template("logout.html")
def do_logout(request):
    request.session.clear()
    if request.GET.get("ret") is None:
        return  redirect(
            to='/'
        )
    else:
        return redirect(
            to=request.GET.get("ret")
        )
