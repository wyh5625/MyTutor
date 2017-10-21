from django.conf.urls import url
from MainPage import views

urlpatterns = [
    url(r'^$', views.HomePageView.as_view()),
]