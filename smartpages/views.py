from django.views.generic import DetailView
from parler.views import TranslatableSlugMixin

from .models import SmartPage


DEFAULT_TEMPLATE = 'smartpages/default.html'


class SmartPageView(TranslatableSlugMixin, DetailView):
    model = SmartPage
    template_name = DEFAULT_TEMPLATE
    slug_field = 'url'
    slug_url_kwarg = 'url'

    def get_language_choices(self):
        return [self.get_language(), 'en']  # TODO: nasty hack!

    def get_object(self, queryset=None):
        slug = self.kwargs[self.slug_url_kwarg]
        if slug[0] != '/':
            self.kwargs[self.slug_url_kwarg] = '/' + slug
        result = super().get_object(queryset)
        return result
