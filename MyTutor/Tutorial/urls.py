from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
app_name = 'Tutorial'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<tutor_id>[0-9]+)/$', views.tutorpage, name='tutorpage'),
]