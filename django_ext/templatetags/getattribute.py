from django import template
from django.conf import settings

register = template.Library()


@register.filter()
def getattribute(value, arg):
    """Gets an attribute of an object dynamically from a string name"""
    if hasattr(value, 'keys') and arg in value:
        result = value[arg]
    elif hasattr(value, str(arg)):
        result = getattr(value, arg)
        if callable(result):
            result = result()
        result = result
    elif arg.isdigit() and len(value) > int(arg):
        result = value[int(arg)]
    else:
        result = settings.TEMPLATE_STRING_IF_INVALID
    return result
