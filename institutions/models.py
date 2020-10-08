from django.db import models
from django.urls import reverse
from ckeditor.fields import RichTextField
from sorl.thumbnail import ImageField
from parler.models import TranslatableModel, TranslatedFieldsModel


class Location(models.Model):
    city = models.CharField(blank=True, max_length=255, )
    country = models.CharField(blank=True, max_length=255, )
    latitude = models.FloatField(null=True, blank=True, )
    longitude = models.FloatField(null=True, blank=True, )

    def __str__(self):
        return ', '.join([self.city, self.country])

    class Meta:
        ordering = ['country', 'city']


class Institution(TranslatableModel):
    name = models.CharField(unique=True, blank=False, max_length=255, help_text='Short (and commonly used) name', )
    slug = models.SlugField(unique=True, blank=False, max_length=255, help_text='The Slug must be unique, and closely match the title for better SEO; it is used as part of the URL.', )
    fullname = models.CharField(max_length=255, blank=True, help_text='If set, the full name will be used in some places instead of the name', )
    location = models.ForeignKey(Location, blank=True, null=True, on_delete=models.CASCADE )
    url = models.URLField(blank=True, null=True, max_length=255, )
    logo = ImageField(null=True, blank=True, upload_to='institutions')
    spacescoop_count = models.IntegerField(default=0, editable=False, )

    @property
    def main_visual(self):
        return self.logo.file if self.logo else None

    @property
    def title(self):
        return self.fullname if self.fullname else self.name

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('partners:detail', kwargs={'slug': self.slug, })

    class Meta:
        ordering = ['name']


class InstitutionTranslation(TranslatedFieldsModel):
    master = models.ForeignKey(Institution, related_name='translations', null=True, on_delete=models.CASCADE)
    description = RichTextField(blank=True, null=True, config_name='small', help_text='Text to appear in Institution page')

    class Meta:
        unique_together = (
            ('language_code', 'master'),
        )
        verbose_name = 'institution translation'


class Person(models.Model):
    name = models.CharField(blank=False, max_length=255)
    citable_name = models.CharField(blank=True, max_length=255, help_text='Required for astroEDU activities')
    email = models.EmailField(blank=False, max_length=255)
    institution = models.ForeignKey(Institution, blank=True, null=True, on_delete=models.CASCADE)
    spaceawe_partner = models.BooleanField(default=False, verbose_name='Space Awareness partner')
    spaceawe_node = models.BooleanField(default=False, verbose_name='Space Awareness node')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
