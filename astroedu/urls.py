from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.conf.urls import url

from django.conf import settings
from django.views.generic import TemplateView, RedirectView
from smartpages.views import SmartPageView
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.conf.urls.i18n import i18n_patterns


from activities.models import Activity, Collection
from search.views import simplesearch
from activities.views import home, about, CollectionListView, CollectionDetailView, markdown_uploader

admin.site.enable_nav_sidebar = False

sitemaps = {
    'activities': Activity.sitemap(priority=0.7),
    'collections': Collection.sitemap(priority=0.6),
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('martor/', include('martor.urls')),
    path('api/uploader/', markdown_uploader, name='markdown_uploader_page'),
    ]

urlpatterns += i18n_patterns(
    path('', home, name='home'),
    path('search/', simplesearch, name='search'),
    # path('^testing/', include('astroedu.testing.urls', namespace='testing')),
    path('activities/', include(('activities.urls','activities'), namespace='activities'),),
    # path('collections/<str:collection_slug>/', CollectionDetailView.as_view(), name='collectionsdetail'),
    path('collections/', include(('activities.urls_collections','collections'), namespace='collections')),

    path('admin/about/', about, name='about'),
    # path('admin/history/', include('djangoplicity.adminhistory.urls', namespace='adminhistory_site')),

    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^page/(?P<url>.*/)$', SmartPageView.as_view(), name='smartpage'),

)

if settings.DEBUG:
    urlpatterns.extend(static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT))
