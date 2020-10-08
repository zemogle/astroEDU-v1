from django.contrib import admin
from .forms import SmartPageForm
from .models import SmartPage, SmartEmbed
from parler.admin import TranslatableAdmin

# from django.utils.translation import ugettext_lazy as _


@admin.register(SmartPage)
class SmartPageAdmin(TranslatableAdmin):
    form = SmartPageForm
    fieldsets = (
        (None, {'fields': ('code', 'url', 'title', 'content', 'release_date' )}),
    )
    # fieldsets = (
    #     (None, {'fields': ('code', 'url', 'title', 'content', )}),
    #     # (_('Advanced options'), {
    #     #     'classes': ('collapse',),
    #     #     'fields': ('registration_required', 'template_name'),
    #     # }),
    # )
    list_display = ('title', 'all_languages_column', )
    # list_filter = ('sites', 'registration_required')
    search_fields = ('title', )
    readonly_fields = ('code', )


@admin.register(SmartEmbed)
class SmartEmbedAdmin(TranslatableAdmin):
    fieldsets = (
        (None, {'fields': ('code', 'content', )}),
    )
    # list_display = ('id', 'code', 'all_languages_column', )
    list_display = ('code', 'all_languages_column', )
    # list_editable = ('code', )
    readonly_fields = ('code', )
