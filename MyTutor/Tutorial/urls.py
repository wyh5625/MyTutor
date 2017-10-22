from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
app_name = 'Tutorial'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^searchTutors/(?P<tutor_id>[0-9]+)/$', views.tutorpage, name='tutorpage'),
    url(r'^myAccount/(?P<user_id>[0-9]+)/$', views.myaccount, name='myaccount'),
    url(r'^message/(?P<user_id>[0-9]+)/$', views.message, name='message'),
]