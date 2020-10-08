from django.conf.urls import url

from activities import views

urlpatterns = [
    url(r'^$', views.JourneyListView.as_view(), name='list'),
]