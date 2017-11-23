from django.conf.urls import url

from . import views
from django.contrib.auth.views import login, logout, password_reset, password_reset_done, password_reset_confirm,password_reset_complete
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import login, logout
app_name = 'Tutorial'
urlpatterns = [
    url(r'^$', views.login, name='home'),
    url(r'^admin/$', views.adminpage, name='adminpage'),
    url(r'^admin/triggersession$', views.triggersession, name='triggersession'),
    url(r'^(?P<myuser_id>[0-9]+)/$', views.index, name='index'),
    url(r'^(?P<myuser_id>[0-9]+)/searchTutors/(?P<tutor_id>[0-9]+)/$', views.tutorpage, name='tutorpage'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/$', views.myaccount, name='myaccount'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/mybooking/$', views.mybooking, name='mybooking'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/mybooking/evaluate/(?P<tutorial_sessions_id>[0-9]+)/$', views.evaluate,
        name='evaluate'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/myprofile/$', views.myprofile, name='myprofile'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/mywallet/$', views.mywallet, name='mywallet'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/mytransaction/$', views.mytransaction, name='mytransaction'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/mywallet/deposit/$', views.deposit, name='deposit'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/mywallet/withdraw/$', views.withdraw, name='withdraw'),
    url(r'^(?P<myuser_id>[0-9]+)/message/$', views.message, name='message'),
    url(r'^(?P<myuser_id>[0-9]+)/timeslot/(?P<tutor_id>[0-9]+)/$', views.selectbooking, name='timeslot'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/mybooking/cancelled/(?P<tutorial_sessions_id>[0-9]+)/$', views.cancelbooking, name='cancelbooking'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register_page, name='register'),
    url(r'^(?P<myuser_id>[0-9]+)/searchTutorName/$', views.search_tutor_name, name='search_tutor_name'),
    url(r'^(?P<myuser_id>[0-9]+)/searchTutorTag/$', views.search_tutor_tag, name='search_tutor_tag'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/tutorTimeslot/(?P<tutor_id>[0-9]+)/$', views.tutorTimeslot, name='tutorTimeslot'),
    url(r'^(?P<myuser_id>[0-9]+)/myAccount/tutorTimeslotSelect/(?P<tutor_id>[0-9]+)/$', views.tutorTimeslotSelecting, name='tutorTimeslotSelecting'),

    #url(r'^registerSuccess/$', views.register_page, name='registerSuccess'),
    #test
]