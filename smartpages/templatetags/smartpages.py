from django import template

from ..models import SmartPage, SmartEmbed

register = template.Library()


@register.simple_tag(takes_context=True)
def smartpage_url(context, value, lang=None):
    try:
        page = SmartPage.objects.get(code=value)
        result = page.get_absolute_url()
    except SmartPage.DoesNotExist:
        result = '/error/SmartPage.DoesNotExist/%s/' % value
    return result


@register.simple_tag(takes_context=True)
def smartembed(context, value, lang=None):
    try:
        embed = SmartEmbed.objects.get(code=value)
        result = embed.content
    except SmartEmbed.DoesNotExist:
        result = '<p>Missing embed: %s</p>' % value
    return result
