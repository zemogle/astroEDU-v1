from django.conf.urls import url

from activities import views

urlpatterns = [
    url(r'^$', views.CollectionListView.as_view(), name='list'),
    url(r'^(?P<collection_slug>[a-zA-Z0-9-]+)/$', views.CollectionDetailView.as_view(), name='detail'),
]
