import re

from django import template
from django.utils.safestring import mark_safe
from django.conf import settings
from sorl.thumbnail import get_thumbnail

register = template.Library()


def _relativise(value, activity, constraint=None):
    new_start = 0
    result = ''
    for m in re.finditer(r'<img src="(.*?)".*?>', value):
        new_src = activity.attachment_url(m.group(1))
        if constraint:
            media_root = settings.MEDIA_ROOT
            if media_root[:-1] != '/':
                media_root += '/'
            path = new_src.replace(settings.MEDIA_URL, media_root)
            resized = get_thumbnail(path, constraint, upscale=False)
            new_src = resized.url
        result += value[new_start:m.start()] + '<img src="%s"/>' % new_src
        new_start = m.end()
    result += value[new_start:]

    result = mark_safe(result)
    return result


@register.filter
def relativise_img_src(value, activity):
    '''Run this filter through some HTML to prepend the local URL to attached images'''
    return _relativise(value, activity)


@register.filter
def relativise_constrain_img_src(value, activity):
    '''Run this filter through some HTML to prepend the local URL to attached images'''
    return _relativise(value, activity, constraint='900')
