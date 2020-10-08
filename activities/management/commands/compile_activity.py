from django.conf import settings

from django_ext.compiler import PublishingBaseCommand


class Command(PublishingBaseCommand):

    help = 'Generate downloads for an activity'

    def __init__(self, *args, **kwargs):
        self.objdef = settings.ACTIVITY_DOWNLOADS
        super().__init__(*args, **kwargs)

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('code', help='Four digit code (YYnn) of the activity')
        parser.add_argument('lang', help='Language of the activity')
        super().add_arguments(parser)
