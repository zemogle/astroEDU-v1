import uuid
import os
from urllib.parse import urlparse
from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models
from django.urls import reverse
from parler.models import TranslatableModel, TranslatedFieldsModel
from parler.managers import TranslatableManager, TranslatableQuerySet
from autoslug import AutoSlugField
from sorl.thumbnail import ImageField

from django_ext.models import PublishingModel, PublishingManager
from django_ext.models.spaceawe import SpaceaweModel
from . import utils
from institutions.models import Institution, Person, Location

from search.mixins import SearchModel


def get_file_path_step(instance, filename):
    return os.path.join('activities/attach', str(instance.hostmodel.uuid), filename)


def get_translated_file_path_step(instance, filename):
    return os.path.join('activities/attach', instance.master.get_current_language(), str(instance.master.hostmodel.uuid), filename)


ACTIVITY_SECTIONS = (
    ('goals', 'Goals'),
    ('objectives', 'Learning Objectives'),
    ('evaluation', 'Evaluation'),
    ('materials', 'Materials'),
    ('background', 'Background Information'),
    ('fulldesc', 'Full Activity Description'),
    ('curriculum', 'Curriculum'),
    ('additional_information', 'Additional Information'),
    ('conclusion', 'Conclusion'),
)

ACTIVITY_METADATA = (
    ('age', 'Age',
        {'display': 'age_range', }),
    ('level', 'Level',
        {'multiple': True, }),
    ('time', 'Time',
        {'display': 'time', }),
    ('group', 'Group',
        {'display': 'group', }),
    ('supervised', 'Supervised',
        {'display': 'supervised', }),
    ('cost', 'Cost per student',
        {'display': 'cost', }),
    ('location', 'Location',
        {'display': 'location', }),
    ('skills', 'Core skills',
        {'multiple': True, }),
    ('learning', 'Type(s) of learning activity',
        {'multiple': True}),
    ('content_area_focus', 'Content Area focus',
     {'display': 'content_area_focus',
      'multiple': True}),
    ('astronomical_scientific_category', 'Astronomical Scientific Categories',
     {'display': 'content_area_focus',
      'multiple': True}),
    ('earth_science_keyword', 'Earth Science keywords',
     {'display': 'content_area_focus',
      'multiple': True}),
    ('space_science_keyword', 'Space Science keywords',
     {'display': 'content_area_focus',
      'multiple': True}),

)

METADATA_OPTION_CHOICES = [(x[0], x[1]) for x in ACTIVITY_METADATA]


class MetadataOption(models.Model):
    group = models.CharField(max_length=50, blank=False, choices=METADATA_OPTION_CHOICES)
    code = models.CharField(max_length=50, blank=False)
    title = models.CharField(max_length=255, blank=False)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['group', 'position']
        unique_together = (('group', 'code'),)

    def __str__(self):
        return self.title


class MetadataOptionsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by('position')


class ActivityQuerySet(TranslatableQuerySet):
    pass


class ActivityManager(PublishingManager, TranslatableManager):
    queryset_class = ActivityQuerySet


class Activity(TranslatableModel, PublishingModel, SpaceaweModel, SearchModel):
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    code = models.CharField(unique=True, max_length=4, help_text='The 4 digit code that identifies the Activity, in the format "YY##": year, folowed by sequential number.')
    doi = models.CharField(blank=True, max_length=50, verbose_name='DOI', help_text='Digital Object Identifier, in the format XXXX/YYYY. See http://www.doi.org/')

    age = models.ManyToManyField(MetadataOption, limit_choices_to={'group': 'age'}, related_name='age+', verbose_name='Age range')
    level = models.ManyToManyField(MetadataOption, limit_choices_to={'group': 'level'}, related_name='level+', help_text='Specify at least one of "Age" and "Level". ', verbose_name='Education level')
    time = models.ForeignKey(MetadataOption, limit_choices_to={'group': 'time'}, related_name='+', on_delete=models.CASCADE)
    group = models.ForeignKey(MetadataOption, limit_choices_to={'group': 'group'}, related_name='+', verbose_name='Group or individual activity', null=True, on_delete=models.CASCADE)
    supervised = models.ForeignKey(MetadataOption, limit_choices_to={'group': 'supervised'}, related_name='+', verbose_name='Supervised for safety', on_delete=models.CASCADE)
    cost = models.ForeignKey(MetadataOption, limit_choices_to={'group': 'cost'}, null=True, verbose_name='Cost per student', on_delete=models.CASCADE)
    location = models.ForeignKey(MetadataOption, limit_choices_to={'group': 'location'}, related_name='+', null=True, on_delete=models.CASCADE)
    skills = models.ManyToManyField(MetadataOption, limit_choices_to={'group': 'skills'}, related_name='skills+', verbose_name='core skills', )
    learning = models.ManyToManyField(MetadataOption, limit_choices_to={'group': 'learning'}, related_name='learning+', verbose_name='type of learning activity', help_text='Enquiry-based learning model')

    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    sourcelink_name = models.CharField(max_length=255, blank=True, verbose_name='Source Name')
    sourcelink_url = models.URLField(max_length=255, blank=True, verbose_name='Source URL')

    # version 9
    affiliation = models.CharField(blank=False, max_length=255, verbose_name='Affiliation or organisation')
    country = models.ForeignKey(Location, verbose_name='Country(s)', null=True, on_delete=models.CASCADE)
    email = models.CharField(max_length=64, verbose_name='Email address of corresponding author')
    suitable_group_size = models.IntegerField(verbose_name='Suitable group size')
    max_number_at_once = models.IntegerField(verbose_name='Maximum number of people at once')
    original_author = models.ForeignKey(Person, blank=True, null=True, verbose_name='Original Author of the activity (if not the authors listed above', on_delete=models.CASCADE)
    language = models.CharField(max_length=64, blank=False, null=False)
    content_area_focus = models.ManyToManyField(MetadataOption, related_name='+', limit_choices_to={'group': 'content_area_focus'}, verbose_name='Content Area focus')

    astronomical_scientific_category = models.ManyToManyField(MetadataOption, related_name='+', limit_choices_to={'group': 'astronomical_categories'}, verbose_name='Astronomical Scientific Categories', blank=True)
    earth_science_keyword = models.ManyToManyField(MetadataOption, related_name='+', limit_choices_to={'group': 'earth_science'}, verbose_name='Earth Science keywords', blank=True)
    space_science_keyword = models.ManyToManyField(MetadataOption, related_name='+', limit_choices_to={'group': 'space_science'}, verbose_name='Space Science keywords', blank=True)
    other_keyword = models.ManyToManyField(MetadataOption, related_name='+', limit_choices_to={'group': 'other'}, verbose_name='Other', blank=True)

    objects = ActivityManager()

    def age_range(self):
        # return ' '.join(obj.title for obj in self.age.all())
        age_ranges = [obj.title for obj in self.age.all()]
        return utils.beautify_age_range(age_ranges)

    def levels_joined(self):
        levels = [obj.title for obj in self.level.all()]
        return ', '.join(levels)

    def skills_joined(self):
        skills = [obj.title for obj in self.skills.all()]
        return ', '.join(skills)

    def author_list(self):
        result = []
        for item in self.authors.all():
            result.append(item.display_name())
        return '; '.join(result)

    def citable_author_list(self):
        result = []
        for item in self.authors.all():
            result.append(item.author.citable_name)
        return '; '.join(result)

    @property
    def main_visual(self):
        result = None
        images = self.attachment_set.filter(main_visual=True)
        if images:
            result = images[0].file
        return result

    @property
    def main_video_link(self):
        video_links = self.link_set.filter(main=True, type=Link.TYPE_VIDEO)
        return video_links.last() if video_links else None

    def is_translation_fallback(self):
        return not self.has_translation(self.language_code)

    @property
    def sourcelink_caption(self):
        return self.sourcelink_name if self.sourcelink_name else self.sourcelink_url

    @classmethod
    def add_prefetch_related(self, qs, prefix=""):
        # # add _after_ qs.filter! see django docs on prefetch_related
        if prefix:
            prefix += '__'
        qs = qs.prefetch_related('%stranslations' % prefix)
        # qs = qs.prefetch_related('{}metadataoption'.format(prefix))
        # qs = qs.prefetch_related('%scategories' % prefix)
        # qs = qs.prefetch_related('%scategories__translations' % prefix)
        # qs = qs.prefetch_related('%simages' % prefix)
        return qs

    def attachment_list(self):
        return self.attachment_set.filter(show=True)

    def languageattachment_list(self):
        return self.languageattachment_set.filter(show=True)

    def metadata_aslist(self):
        result = []
        for meta_code, meta_title, meta_options in ACTIVITY_METADATA:
            value = None
            if meta_options.get('multiple', False):
                values = [x.title for x in getattr(self, meta_code).all()]
                value = ', '.join(values)
            else:
                display_name = meta_options.get('display', meta_code)
                display = getattr(self, display_name)
                if callable(display):
                    value = display()
                elif isinstance(display, MetadataOption):
                    value = display.title
                elif display:
                    value = display

            if value:
                result.append((meta_code, meta_title, value))
        return result

    def attachment_url(self, filename):
        if filename.startswith('http') or filename.startswith('/'):
            result = filename
        else:
            result = os.path.join(settings.MEDIA_URL, 'activities/attach', self.uuid, filename)
        return result

    def __str__(self):
        return '%s - %s' % (self.code, self.title)

    def get_absolute_url(self):
        return reverse('activities:detail', kwargs={'code': self.code, 'slug': self.slug, })

    def get_short_url_full(self):
        if settings.SHORT_NAME == 'astroedu':
            return utils.get_qualified_url('/a/%s' % self.code)
        else:
            return None

    def get_footer_disclaimer(self):
        return 'Go to %s for additional resources and download options of this activity.' % self.get_short_url_full()

    class Meta(PublishingModel.Meta):
        ordering = ['-code']
        verbose_name_plural = 'activities'


class ActivityTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(Activity, related_name='translations', null=True, on_delete=models.CASCADE)
    slug = AutoSlugField(max_length=200, populate_from='title', always_update=True, unique=False)
    title = models.CharField(max_length=255, db_index=True, verbose_name='Activity title', help_text='Title is shown in browser window. Use a good informative title, since search engines normally display the title on their result pages.')
    teaser = models.TextField(blank=False, max_length=140, help_text='250 words', verbose_name='Abstract')
    theme = models.CharField(blank=False, max_length=40, help_text='Use top level AVM metadata')
    keywords = models.TextField(blank=False, help_text='List of keywords, separated by commas')

    acknowledgement = models.CharField(blank=True, max_length=255)

    description = models.TextField(blank=True, verbose_name='brief description', help_text='Maximum 2 sentences! Maybe what and how?')
    goals = models.TextField()
    objectives = models.TextField(verbose_name='Learning Objectives', )
    evaluation = models.TextField(help_text='If the teacher/educator wants to evaluate the impact of the activity, how can she/he do it?')
    materials = models.TextField(blank=True, verbose_name='List of material', help_text='Please indicate costs and/or suppliers if possible')
    background = models.TextField(verbose_name='Background Information', )
    fulldesc = models.TextField(verbose_name='Full description of the activity')
    curriculum = models.TextField(blank=True, verbose_name='Connection to school curriculum', help_text='Please indicate which country')
    additional_information = models.TextField(blank=True, help_text='Notes, Tips, Resources, Follow-up, Questions, Safety Requirements, Variations')
    conclusion = models.TextField()

    alert_message = models.TextField(blank=True, help_text='Alert message, do display at the top of the activity page')

    # version 9
    short_desc_material = models.TextField(blank=True, verbose_name='Short description of Suplementary material')
    further_reading = models.TextField(blank=True, verbose_name='Further reading', default='')
    reference = models.TextField(blank=True, verbose_name='References')

    # Space Awareness fields
    big_idea = models.CharField(max_length=200, blank=True, verbose_name='Big Idea of Science')
    spaceawe_authorship = models.TextField(blank=True, verbose_name='Space Awareness authorship')

    class Meta:
        unique_together = (
            ('language_code', 'master'),
            ('language_code', 'slug')
        )


class AuthorInstitution(models.Model):
    activity = models.ForeignKey(Activity, related_name='authors', on_delete=models.CASCADE)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def display_name(self):
        # there were errors with no existing relations. Now display only relevant data
        display = []
        try:
            display.append(self.author.name)
        except:
            pass
        try:
            display.append(self.institution.name)
        except:
            pass
        return ', '. join(display)

    def __str__(self):
        return self.display_name()


class LanguageAttachment(TranslatableModel):
    main_visual = models.BooleanField(default=False, help_text='The main visual is used as the cover image.')
    show = models.BooleanField(default=False, verbose_name='Show', help_text='Include in attachment list.')
    position = models.PositiveSmallIntegerField(default=0, verbose_name='Position', help_text='Used to define the order of attachments in the attachment list.')
    hostmodel = models.ForeignKey(Activity, on_delete=models.CASCADE)

    def display_name(self):
        if self.title:
            return self.title
        else:
            return os.path.basename(self.file.name)

    def __str__(self):
        return self.display_name()

    class Meta:
        ordering = ['-show', 'position', 'id']


class LanguageAttachmentTranslation(TranslatedFieldsModel):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(blank=True, upload_to=get_translated_file_path_step, )
    master = models.ForeignKey(LanguageAttachment, related_name='translations', null=True, on_delete=models.CASCADE)


class Attachment(models.Model):
    title = models.CharField(max_length=255, blank=True)
    file = models.FileField(blank=True, upload_to=get_file_path_step, )
    main_visual = models.BooleanField(default=False, help_text='The main visual is used as the cover image.')
    show = models.BooleanField(default=False, verbose_name='Show', help_text='Include in attachment list.')
    position = models.PositiveSmallIntegerField(default=0, verbose_name='Position', help_text='Used to define the order of attachments in the attachment list.')
    hostmodel = models.ForeignKey(Activity, on_delete=models.CASCADE)

    def display_name(self):
        if self.title:
            return self.title
        else:
            return os.path.basename(self.file.name)

    def __str__(self):
        return self.display_name()

    class Meta:
        ordering = ['-show', 'position', 'id']


class CollectionQuerySet(TranslatableQuerySet):
    pass


class CollectionManager(PublishingManager, TranslatableManager):
    queryset_class = CollectionQuerySet


class Collection(TranslatableModel, PublishingModel):
    activities = models.ManyToManyField(Activity, related_name='collections', blank=True)
    image = ImageField(null=True, blank=True, upload_to='collections')

    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    objects = CollectionManager()

    @property
    def code(self):
        return self.slug

    @property
    def main_visual(self):
        return self.image.file if self.image else None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
#        tasks.make_thumbnail.delay(self)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('collections:detail', args=[self.slug])

    class Meta(TranslatableModel.Meta):
        pass


class CollectionTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(Collection, related_name='translations', null=True, on_delete=models.CASCADE)
    title = models.CharField(blank=False, max_length=255)
    slug = models.SlugField(unique=True, db_index=True, help_text='Slug identifies the Collection; it is used as part of the URL.')
    description = models.TextField(blank=True, verbose_name='brief description', )


class Repository(models.Model):
    name = models.CharField(max_length=50, blank=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'repositories'


class RepositoryEntry(models.Model):
    repo = models.ForeignKey(Repository, blank=False, null=True, on_delete=models.CASCADE)
    url = models.URLField(blank=False, max_length=255, )
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)

    def __str__(self):
        return '%s - %s' % (self.repo.name, self.url)

    class Meta:
        ordering = ['repo']
        verbose_name_plural = 'repository entries'


class JourneyCategoryQuerySet(TranslatableQuerySet):
    pass


class JourneyCategoryManager(PublishingManager, TranslatableManager):
    queryset_class = JourneyCategoryQuerySet


class JourneyCategory(TranslatableModel, PublishingModel):
    objects = JourneyCategoryManager()

    class Meta:
        verbose_name = "journey category"
        verbose_name_plural = "journey category"


class JourneyCategoryTranslation(TranslatedFieldsModel):

    master = models.ForeignKey(JourneyCategory, related_name='translations', null=True, on_delete=models.CASCADE)
    title = models.CharField(blank=False, max_length=255, verbose_name='Title')
    # description = models.TextField(blank=True, verbose_name='General introduction')
    description = RichTextField(blank=True, null=True, verbose_name='General introduction', config_name='default')


class JourneyChapterQuerySet(TranslatableQuerySet):
    pass


class JourneyChapterManager(TranslatableManager):
    queryset_class = JourneyChapterQuerySet


class JourneyChapter(TranslatableModel):
    """
    There was an idea to make 'The journey of ideas' section in different way than other Activities.
    That's why there is another model/view.
    """
    activities = models.ManyToManyField(Activity, related_name='+', blank=True)
    journey = models.ForeignKey(JourneyCategory, on_delete=models.CASCADE)
    objects = JourneyChapterManager()
    position = models.IntegerField()

    def __str__(self):
        return self.title


class JourneyChapterTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(JourneyChapter, related_name='translations', null=True, on_delete=models.CASCADE)
    title = models.CharField(blank=False, max_length=255, verbose_name='Chapter title')
    description = models.TextField(blank=True, verbose_name='Chapter introduction')

    class Meta:
        unique_together = (
            ('language_code', 'master'),
        )


class LinkQuerySet(TranslatableQuerySet):
    pass


class LinkManager(LinkQuerySet):
    queryset_class = LinkQuerySet


class Link(TranslatableModel):
    TYPE_OTHER = 0
    TYPE_VIDEO = 1

    TYPES = (
        (TYPE_OTHER, 'Other'),
        (TYPE_VIDEO, 'Video')
    )

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    type = models.IntegerField(choices=TYPES, default=TYPE_OTHER)
    main = models.BooleanField(default=False)
    show = models.BooleanField(default=True)
    position = models.IntegerField(default=0)

    def __str__(self):
        return self.title if self.title else self.url

    @property
    def youtube_embed_url(self):
        if self.type != self.TYPE_VIDEO:
            return None
        url = urlparse(self.url)
        if url.netloc == 'www.youtube.com':
            return "{}://{}/embed/{}?controls=1".format(url.scheme, url.netloc, url.query[2:])



class LinkTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(Link, related_name='translations', null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, blank=True)
    url = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = (
            ('language_code', 'master'),
        )
