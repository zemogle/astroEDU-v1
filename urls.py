# -*- coding: utf-8 -*-
from django.urls import path
from django.conf.urls import url, include
from aldryn_django.utils import i18n_patterns
import aldryn_addons.urls
from django.contrib import admin

from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from smartpages.views import SmartPageView
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

from activities.models import Activity, Collection
from astroedu.views import home, about
from astroedu.search.views import simplesearch
from activities.views import CollectionListView, CollectionDetailView
sitemaps = {
    'activities': Activity.sitemap(priority=0.7),
    'collections': Collection.sitemap(priority=0.6),
}

urlpatterns = i18n_patterns(

    path('', home, name='home'),
    path('search/', simplesearch, name='search'),
    # path('^testing/', include('astroedu.testing.urls', namespace='testing')),
    path('activities/', include(('activities.urls','activities'), namespace='activities'),),
    # path('collections/<str:collection_slug>/', CollectionDetailView.as_view(), name='collectionsdetail'),
    path('collections/', include(('activities.urls_collections','collections'), namespace='collections')),

    path('admin/about/', about, name='about'),
    # path('admin/history/', include('djangoplicity.adminhistory.urls', namespace='adminhistory_site')),
    path('admin/', admin.site.urls),

    path('sitemap.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
)

if settings.DEBUG:
    urlpatterns += [
        # test 404 and 500 pages
        url(r'^500/$', TemplateView.as_view(template_name='500.html')),
        url(r'^404/$', TemplateView.as_view(template_name='404.html')),

        # redirects (use nginx rewrite for production)
        url(r'^favicon\.ico/?$', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),

        url(r'^opensearch_desc\.xml/?$', RedirectView.as_view(url='/static/opensearch_desc.xml', permanent=True)),
        url(r'^blog/?$', RedirectView.as_view(url='http://medium.com/@IAUastroedu', permanent=True)),
        url(r'^volunteer/?$', RedirectView.as_view(url='https://unawe.typeform.com/to/UIBI5e', permanent=True)),
        url(r'^a/', include('activities.urls')),
        # serve MEDIA_ROOT (uploaded files) in development
        # url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    ]

urlpatterns += aldryn_addons.urls.patterns() + i18n_patterns(
    *aldryn_addons.urls.i18n_patterns(),  # MUST be the last entry!
    url(r'^(?P<url>.*/)$', SmartPageView.as_view(), name='smartpage')
    # add your own i18n patterns here
)
