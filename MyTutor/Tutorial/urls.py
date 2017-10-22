from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
app_name = 'Tutorial'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^searchTutors/(?P<tutor_id>[0-9]+)/$', views.tutorpage, name='tutorpage'),
    url(r'^myAccount/(?P<user_id>[0-9]+)/$', views.myaccount, name='myaccount'),
    url(r'^myAccount/mybooking/(?P<user_id>[0-9]+)/$', views.mybooking, name='mybooking'),
    url(r'^myAccount/myprofile/(?P<user_id>[0-9]+)/$', views.myprofile, name='myprofile'),
    url(r'^myAccount/mywallet/(?P<user_id>[0-9]+)/$', views.mywallet, name='mywallet'),
    url(r'^message/(?P<user_id>[0-9]+)/$', views.message, name='message'),

]