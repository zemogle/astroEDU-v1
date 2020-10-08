from django.conf import settings


def thumbnail_aliases(request):
    return {'THUMBNAIL_ALIASES': settings.THUMBNAIL_ALIASES}


def site_url(request):
    return {'SITE_URL': settings.SITE_URL}


def texts(request):
    from .models.spaceawe import SECTIONS, CATEGORIES
    return {'SECTIONS': SECTIONS, 'CATEGORIES': CATEGORIES, }
