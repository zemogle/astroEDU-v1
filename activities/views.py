import os
import json
import uuid
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.syndication.views import Feed
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView
from parler.views import ViewUrlMixin, TranslatableSlugMixin

from .utils import get_generated_url
from .models import Activity, Collection, ACTIVITY_SECTIONS, ACTIVITY_METADATA, MetadataOption

from martor.utils import LazyEncoder

import logging
logger = logging.getLogger(__name__)

@login_required
def markdown_uploader(request):
    """
    Makdown image upload for locale storage
    and represent as json to markdown editor.
    """
    if request.method == 'POST' and request.is_ajax():
        if 'markdown-image-upload' in request.FILES:
            image = request.FILES['markdown-image-upload']
            image_types = [
                'image/png', 'image/jpg',
                'image/jpeg', 'image/pjpeg', 'image/gif'
            ]
            if image.content_type not in image_types:
                data = json.dumps({
                    'status': 405,
                    'error': _('Bad image format.')
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            if image.size > settings.MAX_IMAGE_UPLOAD_SIZE:
                to_MB = settings.MAX_IMAGE_UPLOAD_SIZE / (1024 * 1024)
                data = json.dumps({
                    'status': 405,
                    'error': _('Maximum image file is %(size) MB.') % {'size': to_MB}
                }, cls=LazyEncoder)
                return HttpResponse(
                    data, content_type='application/json', status=405)

            img_uuid = "{0}-{1}".format(uuid.uuid4().hex[:10], image.name.replace(' ', '-'))
            tmp_file = os.path.join(settings.MARTOR_UPLOAD_PATH, img_uuid)
            def_path = default_storage.save(tmp_file, ContentFile(image.read()))
            img_url = os.path.join(settings.MEDIA_URL, def_path)

            data = json.dumps({
                'status': 200,
                'link': img_url,
                'name': image.name
            })
            return HttpResponse(data, content_type='application/json')
        return HttpResponse(_('Invalid request!'))
    return HttpResponse(_('Invalid request!'))

def home(request):
    return render(request, 'home.html',
                  {'featured': Activity.objects.featured().active_translations()[0:3],})


@login_required
def about(request):
    import django
    result = 'Django: %s\n' % django.get_version()
    return HttpResponse(result, content_type='text/plain')

def _activity_queryset(request, only_translations=True):
    qs = Activity.objects.available(user=request.user)
    if only_translations:
        qs = qs.active_translations()
    qs = Activity.add_prefetch_related(qs)
    return qs


class ActivityListView(ViewUrlMixin, ListView):
    page_template_name = 'activities/activity_list_page.html'
    view_url_name = 'activities:list'
    paginate_by = 10
    all_categories = 'all'

    def get_queryset(self):
        qs = _activity_queryset(self.request)
        # if category and level is selected, combine filters
        kwargs = self.request.GET
        if self.kwargs.get('category', self.all_categories) != self.all_categories:
            category = self.kwargs['category']
            qs = qs.filter(**{category: True})

        if 'level' in kwargs:
            level = kwargs['level']
            # qs = qs.filter(level__code__in=[level])
            qs = qs.filter(level__code=level)
        if 'age' in kwargs:
            age = kwargs['age']
            qs = qs.filter(age__code=age)
        return qs

    def get_view_url(self):
        if 'level' in self.kwargs:
            return reverse('activities:list_combine', kwargs={'category': self.kwargs.get('category', self.all_categories),
                                                              'level': self.kwargs['level']})
        else:
            return reverse('activities:list_by_category', kwargs={'category': self.kwargs.get('category', self.all_categories)})

    def get_template_names(self):
        if self.request.is_ajax():
            return [self.page_template_name]
        else:
            return super().get_template_names()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['levels'] = MetadataOption.objects.filter(group='level')
        print(context)
        context['sections_meta'] = ACTIVITY_METADATA
        context['page_template'] = self.page_template_name
        context['all_categories'] = self.all_categories
        context['category'] = self.kwargs.get('category', self.all_categories)
        return context


class ActivityDetailView(DetailView):
    slug_field = 'code'
    slug_url_kwarg = 'code'
    view_url_name = 'activities:detail'

    def get_queryset(self, only_translations=False):
        qs = _activity_queryset(self.request, only_translations=only_translations)
        # qs = qs.prefetch_related('originalnews_set')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sections'] = ACTIVITY_SECTIONS
        context['sections_meta'] = ACTIVITY_METADATA
        return context

    def get(self, request, *args, **kwargs):
        fmt = request.GET.get('format')
        if hasattr(settings, 'ACTIVITY_DOWNLOADS') and fmt in settings.ACTIVITY_DOWNLOADS['renderers'].keys():
            code = kwargs[self.slug_url_kwarg]
            url = get_generated_url(settings.ACTIVITY_DOWNLOADS, fmt, code, lang=get_language())
            if not url:
                raise Http404
            return redirect(url)
        else:
            return super().get(request, args, kwargs)

class ActivitybySlug(ActivityDetailView):
    slug_field = 'translations__slug'
    slug_url_kwarg = 'name'

class ActivityDetailPrintView(ActivityDetailView):
    template_name = 'activities/activity_detail_print.html'


class ActivityDetailFirstPagePrintView(ActivityDetailView):
    template_name = 'activities/activity_header_print_pdf_weasy.html'


class ActivityDetailContentPrintView(ActivityDetailView):
    template_name = 'activities/activity_content_print_pdf_weasy.html'


def detail_by_code(request, code):
    'When only the code is provided, redirect to the canonical URL'
    obj = _activity_queryset(request, only_translations=False).get(code=code)
    return redirect(obj, permanent=True)


def detail_by_slug(request, slug):
    'When only the slug is provided, try to redirect to the canonical URL (old style astroEDU URLs)'
    try:
        obj = _activity_queryset(request, only_translations=False).get(translations__slug=slug)
    except Activity.DoesNotExist:
        raise Http404("Activity does not exist")
    return redirect(obj, permanent=True)


class ActivityFeed(Feed):
    title = 'Activities'
    link = '/'
    # link = reverse('scoops:list')
    # description = ''

    def items(self):
        return Activity.objects.available().translated()[:9]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    # item_link is only needed if NewsItem has no get_absolute_url method.
    def item_link(self, item):
        return reverse('activities:detail', kwargs={'code': item.code, 'slug': item.slug})


class CollectionListView(ViewUrlMixin, ListView):
    # template_name = 'activities/collection_list.html'
    # context_object_name = 'object_list'
    model = Collection
    view_url_name = 'collections:list'
    # paginate_by = 10


class CollectionDetailView(TranslatableSlugMixin, DetailView):
    model = Collection
    # template_name = 'activities/collection_detail.html'
    # slug_field = 'slug'
    slug_url_kwarg = 'collection_slug'
