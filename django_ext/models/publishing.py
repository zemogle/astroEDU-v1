from django.db import models
from django.db.models import Q
from django.utils.timezone import now


def publishing_login_required():
    return lambda user: user and user.is_authenticated


def publishing_group_required(group):
    return lambda user: user and user.groups.filter(name=group).exists()


def publishing_permission_required(perm, obj=None):
    return lambda user: user and user.has_perm(perm, obj)


def publishing_user_passes_test(test_func):
    return lambda user: test_func(user)


class PublishingManager(models.Manager):

    def featured(self):
        return self.available().filter(featured=True).order_by('-release_date')

    # I wanted to make this the default Manager, but that's not compatible with django-parler:
    # the TranslatableManager has use_for_related_fields=True
    def available(self, user=None):
        permission_all = self.model.PublishingMeta.permission_all
        permission_embargoed = self.model.PublishingMeta.permission_embargoed
        if permission_all and permission_all(user):
            # retuen all objects
            result = super().get_queryset()
        elif permission_embargoed and permission_embargoed(user):
            # return objects that are either .is_released and .is_embargoed
            q = Q(published=True) & \
                (Q(embargo_date__isnull=True) | Q(embargo_date__lte=now()))
            result = super().get_queryset().filter(q)
        else:
            # only return objects that .is_released
            q = Q(published=True) & \
                Q(release_date__lte=now()) & \
                (Q(embargo_date__isnull=True) | Q(embargo_date__lte=now()))
            result = super().get_queryset().filter(q)
        return result

    def embargoed(self):
        # only return objects that .is_embargoed
        q = Q(published=True) & \
            Q(release_date__gt=now()) & \
            (Q(embargo_date__isnull=True) | Q(embargo_date__lte=now()))
        return super().get_queryset().filter(q)


class PublishingModel(models.Model):
    '''
    IMPORTANT: inherit before other classes.
    This is necessary when another parent class re-defines the default manager (objects) but was not designed to be cooperative.
    see https://rhettinger.wordpress.com/2011/05/26/super-considered-super/
    '''
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    release_date = models.DateTimeField(blank=False)
    embargo_date = models.DateTimeField(blank=True, null=True)

    objects = PublishingManager()

    def is_released(self):
        return self.published and self.release_date <= now() and (self.embargo_date is None or self.embargo_date <= now())
    is_released.short_description = 'released?'
    is_released.boolean = True

    def is_embargoed(self):
        return self.published and self.release_date > now() and (self.embargo_date is None or self.embargo_date <= now())
    is_embargoed.short_description = 'embargoed?'
    is_embargoed.boolean = True

    def not_released_reason(self):
        result = []
        if not self.published:
            result.append('not published')
        if self.release_date > now():
            result.append('staging (release date in the future)')
        if self.is_embargoed():
            result.append('under embargo')
        return result

    @classmethod
    def sitemap(cls, priority=None):
        from django.contrib.sitemaps import GenericSitemap
        object_list = {
            'queryset': cls.objects.available(),  #TODO make sure this only shows _released objects
            'date_field': 'modification_date',
        }
        return GenericSitemap(object_list, priority=priority)

    class Meta:
        abstract = True
        ordering = ['-release_date']

    class PublishingMeta:
        permission_all = publishing_login_required()  # how to determine if a user can access all items
        permission_embargoed = None  # how to determine if a user can access embargoed items
