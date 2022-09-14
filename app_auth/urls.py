from django.urls import path,re_path
from . import views
from django.conf.urls.static import static
import web.settings
from  django.conf.urls import url
import os
urlpatterns = [
    url('login', views.do_login, name='views.do_login'),
    url('logout', views.do_logout, name='views.do_logout'),

]