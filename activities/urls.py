from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
    path('', views.ActivityListView.as_view(), name='list'),
    path('feed/', views.ActivityFeed(), name='feed'),
    path('<int:code>/', views.ActivityDetailView.as_view(), name='detail-code'),
    path('<int:code>/print-preview/', views.ActivityDetailPrintView.as_view(), name='print-preview'),

    # for PDF generator I need first page separated from other pages
    path('<int:code>/first-page-print-preview/', views.ActivityDetailFirstPagePrintView.as_view(), name='print-preview-header'),
    path('<int:code>/content-print-preview/', views.ActivityDetailContentPrintView.as_view(), name='print-preview-content'),

    path('<int:code>/<slug:name>/', views.ActivityDetailView.as_view(), name='detail'),
    path('<slug:name>/', views.ActivitybySlug.as_view(), name='detail-slug'),  # old style astroEDU URL
    # needed ActivityListView.get_view_url, but really is spaceawe specific:
    path('category/<str:category>/', views.ActivityListView.as_view(), name='list_by_category'),
    ]
