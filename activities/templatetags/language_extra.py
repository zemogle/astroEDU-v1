from django import template
from django.template.defaultfilters import stringfilter
from django.conf import settings

register = template.Library()

@register.filter
@stringfilter
def language_long(code):
    lang = {l[0]:l[1] for l in settings.LANGUAGES}
    return lang[code]
