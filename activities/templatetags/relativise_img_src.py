import re
import logging

from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
from easy_thumbnails.files import get_thumbnailer

from django.core.files.storage import default_storage

register = template.Library()

logger = logging.getLogger('django')

def _relativise(value, activity, constraint=None):
    new_start = 0
    result = ''
    for m in re.finditer(r'src="(.*?)".*?>', value):
        new_src = activity.attachment_url(m.group(1))
        media_root = settings.MEDIA_ROOT
        if media_root[:-1] != '/':
            media_root += '/'
        path = new_src.replace("http://astroedu.iau.org/",'').replace('media/','')
        try:
            new_src = default_storage.url(path)
        except:
            new_src = "https://via.placeholder.com/200x200?text=No+Image"
        logger.critical(new_src)
        result += value[new_start:m.start()] + '<img src="%s"/>' % new_src
        new_start = m.end()
    result += value[new_start:]
    # result = mark_safe(result)
    return result


@register.filter
def relativise_img_src(value, activity):
    '''Run this filter through some HTML to prepend the local URL to attached images'''
    return _relativise(value, activity)


@register.filter
def relativise_constrain_img_src(value, activity):
    '''Run this filter through some HTML to prepend the local URL to attached images'''
    return _relativise(value, activity, constraint='900')
