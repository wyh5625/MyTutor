from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import login, logout
app_name = 'Tutorial'
urlpatterns = [
    url(r'^$', views.index, name='home'),
    url(r'^(?P<student_id>[0-9]+)/$', views.index, name='index'),
    url(r'^(?P<student_id>[0-9]+)/searchTutors/(?P<tutor_id>[0-9]+)/$', views.tutorpage, name='tutorpage'),
    url(r'^(?P<user_id>[0-9]+)/myAccount/$', views.myaccount, name='myaccount'),
    url(r'^(?P<user_id>[0-9]+)/myAccount/mybooking/$', views.mybooking, name='mybooking'),
    url(r'^(?P<user_id>[0-9]+)/myAccount/myprofile/$', views.myprofile, name='myprofile'),
    url(r'^(?P<user_id>[0-9]+)/myAccount/mywallet/$', views.mywallet, name='mywallet'),
    url(r'^(?P<user_id>[0-9]+)/message/$', views.message, name='message'),
    url(r'^(?P<student_id>[0-9]+)/timeslot/(?P<tutor_id>[0-9]+)/$', views.selectbooking, name='timeslot'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
]