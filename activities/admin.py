import re
from urllib.parse import urljoin
import unicodecsv

from django import forms
from django.urls import reverse
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from parler.forms import TranslatableModelForm

from martor.widgets import AdminMartorWidget

from .models import Activity, ActivityTranslation, Attachment, LanguageAttachment, \
    AuthorInstitution, MetadataOption, Collection, RepositoryEntry, Repository, Location, Link


class MetadataOptionAdmin(admin.ModelAdmin):
    model = MetadataOption
    list_display = ('code', 'title', 'group', 'position', )
    list_editable = ('position', )
    list_filter = ('group',)

    def has_add_permission(self, request):
        return False


class ActivityAttachmentInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return

        # There can be only one "main visual"
        main_visual_count = 0
        for form in self.forms:
            if form.cleaned_data:
                main_visual = form.cleaned_data['main_visual']
                if main_visual:
                    main_visual_count += 1

        if main_visual_count > 1:
            raise forms.ValidationError('There can be only one "main visual".')


class AuthorInstitutionInline(admin.TabularInline):
    model = AuthorInstitution
    verbose_name = 'author'
    verbose_name_plural = 'authors'
    min_num = 1
    extra = 1


class ActivityAttachmentInline(admin.TabularInline):
    model = Attachment
    formset = ActivityAttachmentInlineFormset
    fields = ('title', 'file', 'main_visual', 'show', 'position', )


class ActivityLanguageAttachmentInline(TranslatableTabularInline):
    model = LanguageAttachment
    fields = ('title', 'file', 'main_visual', 'show', 'position', )


class RepositoryEntryInline(admin.TabularInline):
    model = RepositoryEntry


class LinkInline(TranslatableTabularInline):
    model = Link
    fields = ('title', 'url', 'type', 'description', 'main', 'show', 'position', )


class ActivityAdminForm(TranslatableModelForm):
    class Meta:
        model = Activity
        fields = ('code', 'title', 'release_date', 'published', 'featured', 'space', 'earth', 'navigation', 'heritage', 'sourcelink_name', 'sourcelink_url')
        widgets = {
            'time': forms.RadioSelect,
            'group': forms.RadioSelect,
            'supervised': forms.RadioSelect,
            'cost': forms.RadioSelect,
            'location': forms.RadioSelect,
        }

    def clean_code(self):
        code = self.cleaned_data['code']
        if not re.match('^\w*\d{4}$', code):
            raise forms.ValidationError('The code should be four digits, in the format: YY##')
        return code

    def clean_teaser(self):
        teaser = self.cleaned_data['teaser']
        teaser = teaser.replace('\n', ' ').strip()
        return teaser

    def clean(self):
        cleaned_data = super().clean()

        age = cleaned_data.get('age')
        level = cleaned_data.get('level')
        if not age and not level:
            raise forms.ValidationError('Please fill in at least one of these fields: "Age", "Level"')

        return cleaned_data


class MembershipInline(admin.TabularInline):
    model = Collection.activities.through


class ActivityAdmin(TranslatableAdmin):
    form = ActivityAdminForm

    def view_on_site(self, obj):
        return obj.get_absolute_url()

    def view_link(self, obj):
        return mark_safe('<a href="%s">View</a>' % obj.get_absolute_url())

    def get_countries(self):
        return Location.objects.distinct('country').values('id', 'country')

    def default_title(self, obj):
        return obj.safe_translation_getter('title', any_language=True)


    view_link.short_description = ''
    view_link.allow_tags = True

    counted_fields = ('teaser', )

    form = ActivityAdminForm
    list_display = ('code', 'default_title', 'all_languages_column', 'author_list', 'published', 'release_date', 'is_released', 'featured', 'doi', 'view_link', )  # , 'thumb_embed', 'list_link_thumbnail', view_link('activities'))
    list_editable = ('published', 'featured', )
    ordering = ('-release_date', )
    date_hierarchy = 'release_date'
    list_filter = ('age', 'level', 'time', 'group', 'supervised', 'cost', 'location')

    inlines = [AuthorInstitutionInline, ActivityAttachmentInline, ActivityLanguageAttachmentInline, RepositoryEntryInline, MembershipInline, LinkInline]

    # activities is shared model, but on astroedu is needed modified fieldset
    fieldsets = [
        (None,
         {'fields': ('code', 'title',)}),
        ('Publishing',
         {'fields': ('published', 'featured', 'pdf', ('release_date', 'embargo_date'),),}),
        (None,
         {'fields': (
             ('age', 'level',), ('time', 'group', 'supervised', 'cost',), ('location', 'skills', 'learning',),
             'suitable_group_size', 'max_number_at_once',
             'keywords', 'affiliation', 'country', 'email', 'original_author', 'language')}),
        ('Content Area focus',
         {'fields': ('content_area_focus', )}),
        ('Specific Content Category/s',
         {'fields': ('astronomical_scientific_category', 'earth_science_keyword', 'space_science_keyword', 'other_keyword')}),

        ('Description',
         {'fields': (
             'teaser', 'materials', 'goals', 'objectives', 'evaluation', 'background',)}),
        (None,
         {'fields': ('fulldesc', 'short_desc_material')}),
        (None,
         {'fields': ('curriculum', 'additional_information', 'conclusion', 'further_reading', 'reference')}),
    ]



    readonly_fields = ('is_released', )
    formfield_overrides = {
        models.ManyToManyField: {'widget': forms.CheckboxSelectMultiple},
        models.TextField: {'widget': AdminMartorWidget},
    }

    fieldsets_and_inlines_order = ('f', 'f', 'i', )  # order of fields: first fieldset, then first inline, then everything else as usual

    # class Media:
    #     js = [
    #         '/static/js/admin.js',
    #     ]


class CollectionAdminForm(TranslatableModelForm):
    pass


class CollectionAdmin(TranslatableAdmin):
    form = CollectionAdminForm

    def view_link(self, obj):
        return '<a href="%s">View</a>' % obj.get_absolute_url()

    view_link.short_description = ''
    view_link.allow_tags = True

    list_display = ('title', 'slug', 'view_link', )

    fieldsets = [
        (None, {'fields': ('title', 'slug', )}),
        ('Publishing', {'fields': ('published', 'featured', ('release_date', 'embargo_date'), ), }),
        ('Contents', {'fields': ('description', 'image', )}),
    ]


admin.site.register(Collection, CollectionAdmin)
ActivityAdmin.fieldsets = ActivityAdmin.fieldsets[0:1] + [
    (None,
        {'fields': ('acknowledgement', 'doi', )}),
    ] + ActivityAdmin.fieldsets[1:]




admin.site.site_header = "astroEDU Admin"
admin.site.site_title = "astroEDU Admin Portal"

admin.site.register(MetadataOption, MetadataOptionAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Repository)
