from django.conf import settings

from django_ext.compiler import PublishingBaseCommand


class Command(PublishingBaseCommand):

    help = 'Generate downloads for a Space Scoop article'

    def __init__(self, *args, **kwargs):
        self.objdef = settings.SPACESCOOP_DOWNLOADS
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('code', help='Four digit code (YYnn) of the article')
        parser.add_argument('lang', help='Language of the article')
        super().add_arguments(parser)
