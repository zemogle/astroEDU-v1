import re
from urllib.parse import urljoin
import unicodecsv

from django import forms
from django.urls import reverse
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.http import HttpResponse
from django.utils.translation import ugettext as _
from parler.admin import TranslatableAdmin, TranslatableTabularInline
from parler.forms import TranslatableModelForm
from django_mistune import markdown

from activities.utils import bleach_clean
from .models import Activity, Attachment, LanguageAttachment, AuthorInstitution, MetadataOption, Collection, RepositoryEntry, Repository, JourneyCategory, JourneyChapter, Location, Link


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
        fields = ('code', 'title', 'release_date', 'published', 'featured', 'description', 'short_desc_material', 'materials', 'further_reading', 'goals', 'objectives', 'background', 'fulldesc', 'evaluation', 'curriculum', 'additional_information', 'conclusion', 'space', 'earth', 'navigation', 'heritage', 'sourcelink_name', 'sourcelink_url', )
        widgets = {
            'time': forms.RadioSelect,
            'group': forms.RadioSelect,
            'supervised': forms.RadioSelect,
            'cost': forms.RadioSelect,
            'location': forms.RadioSelect,
            'teaser': forms.TextInput(attrs={'class': 'vTextField'}),
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

        for fieldname in ('description', 'materials', 'goals', 'objectives', 'background', 'fulldesc', 'evaluation', 'curriculum', 'additional_information', 'conclusion', ):
            value = cleaned_data.get(fieldname)
            value = bleach_clean(value)  # sanitize html embed in markdown
            cleaned_data[fieldname] = value
            try:
                markdown(value)
            except:
                # TODO: test error logging!
                import sys
                e = sys.exc_info()[0]
                print(e)
                self.add_error(fieldname, _('Markdown error'))

        return cleaned_data


class MembershipInline(admin.TabularInline):
    model = Collection.activities.through


def activities_csv(modeladmin, request, queryset):
    from django.utils import translation

    header = [
        'URL location of the English version of this activity',
        'URL location of the French version of this activity',
        'URL location of the German version of this activity',
        'URL location of the other language versions of this activity',
        'URL of the thumbnail',
        'Activity title',
        'Age',
        'Time',
        'Groupsize (group/individual)',
        'Level',
        'Cost',
        'Supervised',
        'Location',
        'Core skills',
        'Type of learning activity',
        'Keywords',
        'Big idea of science',
        'Theme',
        'Teaser',
        'Brief description',
        'Goals',
        'Learning objectives',
        'Evaluation',
        'Materials',
        'Background information',
        'Full Activity description',
        'Connection to school  curriculum',
        'Additional information',
        'Conclusion',
        'Space Awareness authorship',
        'Source name',
        'Source URL',
        'URL to additional documents (attachments), English',
        'URL to additional documents (attachments), other languages'
    ]

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=activities.csv'

    writer = unicodecsv.writer(response, encoding='utf-8')
    writer.writerow(header)

    for activity in queryset:
        activity.set_current_language('en')
        translation.activate('en')
        url = urljoin(settings.SITE_URL,
                      reverse('activities:detail', kwargs={'code': activity.code, 'slug': activity.slug}))

        if activity.has_translation('fr'):
            translation.activate('fr')
            activity.set_current_language('fr')
            url_fr = urljoin(settings.SITE_URL,
                            reverse('activities:detail', kwargs={'code': activity.code, 'slug': activity.slug}))
        else:
            url_fr = ''

        if activity.has_translation('de'):
            translation.activate('de')
            activity.set_current_language('de')
            url_de = urljoin(settings.SITE_URL,
                             reverse('activities:detail', kwargs={'code': activity.code, 'slug': activity.slug}))
        else:
            url_de = ''
        url_others_list = []
        for language_code, language_name in settings.LANGUAGES:
            if language_code not in ['en', 'fr', 'de'] and activity.has_translation(language_code):
                translation.activate('en')
                activity.set_current_language(language_code)
                url_others_list.append(urljoin(settings.SITE_URL, reverse('activities:detail',
                                                                          kwargs={'code': activity.code,
                                                                                  'slug': activity.slug})))
        activity.set_current_language('en')

        row = [
            url,
            url_fr,
            url_de,
            ','.join(url_others_list),
            activity.title,
            ','.join(activity.age.values_list('title', flat=True).all()),
            activity.time.title if activity.time else '',
            activity.group.title if activity.group else '',
            ','.join(activity.level.values_list('title', flat=True).all()),
            activity.cost.title if activity.cost else '',
            activity.supervised.title if activity.supervised else '',
            ','.join(activity.skills.values_list('title', flat=True).all()),
            activity.learning.title if activity.learning else '',
            activity.keywords,
            activity.big_idea,
            activity.theme,
            activity.teaser,
            activity.description,
            activity.goals,
            activity.objectives,
            activity.evaluation,
            activity.materials,
            activity.background,
            activity.fulldesc,
            activity.curriculum,
            activity.additional_information,
            activity.conclusion,
            activity.spaceawe_authorship,
            activity.sourcelink_name,
            activity.sourcelink_url,
            '',
            ''
        ]

        writer.writerow(row)
    return response


activities_csv.short_description = "Generate CSV from activities"


class ActivityAdmin(TranslatableAdmin):

    def view_on_site(self, obj):
        return obj.get_absolute_url()

    def view_link(self, obj):
        return '<a href="%s">View</a>' % obj.get_absolute_url()

    def get_countries(self):
        return Location.objects.distinct('country').values('id', 'country')

    view_link.short_description = ''
    view_link.allow_tags = True

    counted_fields = ('teaser', )

    form = ActivityAdminForm
    list_display = ('code', 'title', 'all_languages_column', 'author_list', 'published', 'release_date', 'is_released', 'featured', 'doi', 'view_link', )  # , 'thumb_embed', 'list_link_thumbnail', view_link('activities'))
    list_editable = ('published', 'featured', )
    ordering = ('-release_date', )
    date_hierarchy = 'release_date'
    list_filter = ('age', 'level', 'time', 'group', 'supervised', 'cost', 'location')
    actions = [activities_csv]

    inlines = [AuthorInstitutionInline, ActivityAttachmentInline, ActivityLanguageAttachmentInline, RepositoryEntryInline, MembershipInline, LinkInline]

    # activities is shared model, but on astroedu is needed modified fieldset
    fieldsets = [
        (None,
         {'fields': ('code', 'title',)}),
        ('Publishing',
         {'fields': ('published', 'featured', ('release_date', 'embargo_date'),),}),
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
    }

    fieldsets_and_inlines_order = ('f', 'f', 'i', )  # order of fields: first fieldset, then first inline, then everything else as usual

    class Media:
        js = [
            'http://ajax.googleapis.com/ajax/libs/jquery/1.7/jquery.min.js',
            '/static/js/admin.js',
        ]


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



class JourneyChapterInlineAdmin(TranslatableTabularInline):
    model = JourneyChapter
    extra = 1

    fields = ('title', 'description', 'activities')
    raw_id_fields = ('activities', )
    inlines = ('activities', )


class JourneyAdmin(TranslatableAdmin):
    inlines = [JourneyChapterInlineAdmin]

    fieldsets = [
        (None,
         {'fields': ('title', 'description',)}),
        ('Publishing',
         {'fields': ('published', 'featured', ('release_date', 'embargo_date'),), }),
    ]

    list_display = ('title', 'published')



admin.site.site_header = "astroEDU Admin"
admin.site.site_title = "astroEDU Admin Portal"

admin.site.register(JourneyCategory, JourneyAdmin)
admin.site.register(MetadataOption, MetadataOptionAdmin)
admin.site.register(Activity, ActivityAdmin)
admin.site.register(Repository)
