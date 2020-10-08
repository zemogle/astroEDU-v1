import os

from django.db import models
from django.core import validators


def upload_to(instance, filename):
    if instance.folder:
        return os.path.join('files', instance.folder.title, filename)
    else:
        return os.path.join('files', filename)


class Folder(models.Model):
    title = models.CharField(unique=True, blank=False, max_length=255, help_text='Please use only alphabetic characters, numbers, and "-", "_" and "/"',
                             validators=[validators.RegexValidator(regex='^[-a-zA-Z0-9_/]+$')])

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class File(models.Model):
    title = models.CharField(blank=True, max_length=255, help_text='Leave blank to use filename')
    # file = models.FileField(blank=False, upload_to='files', )
    file = models.FileField(blank=False, upload_to=upload_to, )
    folder = models.ForeignKey(Folder, blank=True, null=True, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.folder:
            return self.folder.title + '/' + self.title
        else:
            return self.title

    class Meta:
        ordering = ['title']
