import os

from django.db import models
from django.utils.translation import ugettext_lazy as _


class BaseAttachmentModel(models.Model):

    title = models.CharField(max_length=255, blank=True)
    show = models.BooleanField(default=False, verbose_name=u'Show', help_text='Include in attachment list.')
    position = models.PositiveSmallIntegerField(default=0, verbose_name='Position', help_text='Used to define the order of attachments in the attachment list.')
    # hostmodel = None  # must be set by concrete class! e.g.: models.ForeignKey(Activity)

    def display_name(self):
        if self.title:
            return self.title
        elif self.file:
            return os.path.basename(self.file.name)
        else:
            return os.path.basename(self.file.name)

    def __str__(self):
        return self.display_name()

    class Meta:
        abstract = True
        ordering = ['position', 'id']


# class MediaAttachedModel(models.Model):

#     # #TODO: simplify media_key: make it a constant string property of the concrete class, and remove most of MediaAttachedModel ?
#     # @classmethod
#     # def media_key(cls):
#     #     return str(cls._meta.verbose_name_plural)

#     # def media_url(self, resource, ext):
#     #     if self.main_visual:
#     #         return os.path.join(settings.MEDIA_URL, self.media_key(), resource, self.code) + '.' + ext

#     #TODO: self.SIZES
#     #TODO: 'jpg' magic number
#     # def __getattribute__(self, name):
#     #     # handles calls to e.g. 'thumb_url'
#     #     if name[-4:] == '_url' and name[:-4] in self.SIZES:
#     #         return self.media_url(name[:-4], 'jpg')
#     #     else:
#     #         return super().__getattribute__(name)

#     @property
#     def main_visual(self):
#         result = None
#         images = self.images.all()
#         if images:
#             result = images[0].file
#         return result

#     # def image_list(self):
#     #     return self.images.filter(show=True)

#     # def attachment_list(self):
#     #     return self.attachment_set.filter(show=True)

#     class Meta:
#         abstract = True
