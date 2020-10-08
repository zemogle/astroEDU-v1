# from django import template
# from django.conf import settings

# register = template.Library()


# @register.filter
# def spaceawe_category(value):
#     result = value
#     # for (x, y) in SPACEAWE_CATEGORY_CHOICES:
#     #     if value == x:
#     #         result = y
#     rs = [y for (x, y) in settings.SPACEAWE_CATEGORY_CHOICES if x == value]
#     if rs:
#         result = rs[0]
#     return result
