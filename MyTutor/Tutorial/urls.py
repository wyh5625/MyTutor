from django.conf.urls import url
from Tutorial import views

urlpatterns = [
    url(r'^$', views.HomePageView.as_view()),
]