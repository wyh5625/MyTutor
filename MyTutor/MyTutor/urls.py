"""MyTutor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
	url(r'^Tutorial/', include('Tutorial.urls')),
    url(r'^accounts/login', RedirectView.as_view(url='/Tutorial/login')),
    url(r'^password_reset/$', auth_views.password_reset, {
        'post_reset_redirect': 'done/'
    }, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',auth_views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.password_reset_complete, name='password_reset_complete'),

	#rl(r'^Tutorial/login/$', auth_views.login, name='login'),
    #url(r'^Tutorial/logout/$', auth_views.logout, {'next_page': '/Tutorial/searchTutor/'}, name='logout'),
    #url(r'^Tutorial/searchTutors/', include('Tutorial.urls')),  #when someone clicks search tutor
]
