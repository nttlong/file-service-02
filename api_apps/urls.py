from django.urls import path
from django.conf.urls import include, url
from . import views

urlpatterns = (
    url(r'(?P<app_name>[\w\-]+)/register', views.create_app, name='create_app'),
    url(r'(?P<app_name>[\w\-]+)/list$', views.list_apps, name='list_app'),
    url(r'(?P<app_name>[\w\-]+)/get$', views.get_app, name='get_app'),
)