from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import get_script_prefix, reverse
from django.utils.encoding import iri_to_uri

from parler.models import TranslatableModel, TranslatedFieldsModel
from parler.managers import TranslatableManager, TranslatableQuerySet
from ckeditor.fields import RichTextField

from django_ext.models import PublishingModel, PublishingManager


class SmartPageQuerySet(TranslatableQuerySet):
    pass


class SmartPageManager(PublishingManager, TranslatableManager):
    queryset_class = SmartPageQuerySet


class SmartPage(PublishingModel, TranslatableModel):
    code = models.CharField(unique=True, max_length=100, blank=True, db_index=True, help_text='Internal code to identify the page; if set, do not modify. When in doubt, leave empty.')
    # template_name = models.CharField(_('template name'), max_length=70, blank=True,
    #     help_text="Example: 'smartpages/contact_page.html'. If this isn't provided, the system will use 'smartpages/default.html'."
    #     ),
    # )
    registration_required = models.BooleanField(
        _('registration required'),
        help_text='If this is checked, only logged-in users will be able to view the page.',
        default=False)
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    objects = SmartPageManager()

    class Meta:
        # ordering = ('translations__url',)
        verbose_name = 'page'

    def __str__(self):
        return 'SmartPage: %s -- %s' % (self.url, self.title)

    # def get_absolute_url(self):
    #     # Handle script prefix manually because we bypass reverse()
    #     return iri_to_uri(get_script_prefix().rstrip('/') + self.url)

    def get_absolute_url(self):
        return reverse('smartpage', kwargs={'url': self.url.lstrip('/'), })


class SmartPageTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(SmartPage, related_name='translations', null=True, on_delete=models.CASCADE)
    url = models.CharField('URL', max_length=100, db_index=True, help_text='Example: "/about/contact/". Make sure to have leading and trailing slashes.')
    title = models.CharField('title', max_length=200)
    content = RichTextField('content', blank=True, config_name='smartpages', )

    class Meta:
        unique_together = (
            ('language_code', 'master'),
            ('language_code', 'url'),
        )
        verbose_name = 'page translation'


class SmartEmbed(TranslatableModel):
    code = models.CharField(unique=True, max_length=100, blank=True, db_index=True, help_text='Internal code to identify the embed; if set, do not modify. When in doubt, leave empty.')
    creation_date = models.DateTimeField(auto_now_add=True, null=True)
    modification_date = models.DateTimeField(auto_now=True, null=True)

    class Meta:
        ordering = ('code',)
        verbose_name = 'embed'

    def __str__(self):
        return "SmartEmbed: %s" % self.code


class SmartEmbedTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(SmartEmbed, related_name='translations', null=True, on_delete=models.CASCADE)
    content = RichTextField('content', blank=True, config_name='smartpages', )

    class Meta:
        unique_together = (
            ('language_code', 'master'),
        )
        verbose_name = 'embed translation'
