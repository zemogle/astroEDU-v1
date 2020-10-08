from django.core.management.base import BaseCommand
from django.conf import settings

from activities.compile import make_pdf


class Command(BaseCommand):
    help = 'Generates PDF for the specified activities'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('code', help='Four digit code (YYnn) of the article')
        parser.add_argument('lang', help='Language of the article')

        # Named (optional) arguments
        parser.add_argument(
            '--site-url',
            action='store',
            dest='site_url',
            default=None,
            help='Connect to a website other than %s' % settings.SITE_URL)

    def handle(self, *args, **options):
        code = options['code']
        lang = options['lang']
        make_pdf(code, lang, site_url=options['site_url'])
