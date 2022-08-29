from django.urls import path,re_path
from django.conf.urls import include, url
from . import views
from django.conf.urls.static import static
import web.settings
import os
urlpatterns = [
    url(r'(?P<full_path>)', views.index, name='index')

]