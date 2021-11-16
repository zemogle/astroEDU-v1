from django.contrib import admin
from django.db import models
from pagedown.widgets import AdminPagedownWidget
from parler.admin import TranslatableAdmin

from .forms import SmartPageForm
from .models import SmartPage, SmartEmbed


@admin.register(SmartPage)
class SmartPageAdmin(TranslatableAdmin):
    form = SmartPageForm
    fieldsets = (
        (None, {'fields': ('code', 'url', 'title', 'content', 'release_date' )}),
    )

    list_display = ('title', 'all_languages_column', 'code' )
    search_fields = ('title', )
    # readonly_fields = ('code', )



@admin.register(SmartEmbed)
class SmartEmbedAdmin(TranslatableAdmin):
    fieldsets = (
        (None, {'fields': ('code', 'content', )}),
    )
    # list_display = ('id', 'code', 'all_languages_column', )
    list_display = ('code', 'all_languages_column', )
    # list_editable = ('code', )
    readonly_fields = ('code', )
