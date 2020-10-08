import os
import time
import importlib

# from django.template import loader, Context, Template
from django.conf import settings
from django.core.management.base import BaseCommand

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger('spaceawe')


def get_python_thing(fullname):
    module_name, thing_name = fullname.rsplit('.', 1)
    module = importlib.import_module(module_name)
    return getattr(module, thing_name)


def generate_one(objdef, obj, file_type, force=False, site_url=None):
    ctx = {'slug': obj.slug, 'code': obj.code, 'ext': file_type}
    if hasattr(obj, 'language_code'):
        ctx['lang'] = obj.language_code
    filename = objdef['filename_tpl'] % ctx
    path = os.path.join(settings.MEDIA_ROOT, objdef['path'], filename)
    if force or (not (os.path.exists(path) and os.path.getmtime(path) > time.mktime(obj.modification_date.timetuple()))):
        if not site_url:
            site_url = settings.SITE_URL
        renderer = get_python_thing(objdef['renderers'][file_type])
        renderer(obj, path, site_url=site_url)
    return filename


def get_generated_url(objdef, file_type, code, lang=None):
    model = get_python_thing(objdef['model'])
    if lang:
        obj = model.objects.available().language(lang).get(code=code)
    else:
        obj = model.objects.available().get(code=code)
    filename = generate_one(objdef, obj, file_type)
    return settings.MEDIA_URL + objdef['path'] + filename


def generate_career(objdef, obj, file_type, force=False, site_url=None):
    ctx = {'slug': obj.slug, 'id': obj.id, 'ext': file_type}
    if hasattr(obj, 'language_code'):
        ctx['lang'] = obj.language_code
    filename = objdef['filename_tpl'] % ctx
    path = os.path.join(settings.MEDIA_ROOT, objdef['path'], filename)
    if force or not (os.path.exists(path)):
        if not site_url:
            site_url = settings.SITE_URL
        renderer = get_python_thing(objdef['renderers'][file_type])
        renderer(obj, path, site_url=site_url)
    return filename


def get_career_generated_url(objdef, file_type, career_id, lang=None):
    model = get_python_thing(objdef['model'])
    if lang:
        obj = model.objects.available().language(lang).get(id=career_id)
    else:
        obj = model.objects.available().get(id=career_id)
    filename = generate_career(objdef, obj, file_type)
    return settings.MEDIA_URL + objdef['path'] + filename


LANGUAGES = [code for (code, name) in settings.LANGUAGES]


def _generate_formats(objdef, obj, formats, force, site_url):
    for fmt in formats:
        generate_one(objdef, obj, fmt, force=force, site_url=site_url)


def generate(objdef, options):
    model = get_python_thing(objdef['model'])
    code = options['code']
    lang = options['lang']
    force = options['force']
    site_url = options['site_url']

    formats = [fmt for fmt in settings.ACTIVITY_DOWNLOADS['renderers'].keys() if options[fmt]]

    if code == 'all':
        if lang == 'all':
            for baseobj in model.objects.available():
                for lang in baseobj.get_available_languages():
                    if lang in LANGUAGES:
                        obj = model.objects.available().language(lang).get(code=baseobj.code)
                        _generate_formats(objdef, obj, formats, force, site_url)
        else:
            for obj in model.objects.available().language(lang):
                _generate_formats(objdef, obj, formats, force, site_url)

    else:
        if lang == 'all':
            baseobj = model.objects.available().get(code=code)
            for lang in baseobj.get_available_languages():
                if lang in LANGUAGES:
                    obj = model.objects.available().language(lang).get(code=code)
                    _generate_formats(objdef, obj, formats, force, site_url)

        else:
            obj = model.objects.available().language(lang).get(code=code)
            _generate_formats(objdef, obj, formats, force, site_url)


class PublishingBaseCommand(BaseCommand):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.formats = self.objdef['renderers'].keys()

    def add_arguments(self, parser):
        # Named (optional) arguments
        for fmt in self.formats:
            parser.add_argument(
                '--%s' % fmt,
                action='store_true',
                dest=fmt,
                default=False,
                help='Generate only %s file' % fmt)
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=None,
            help='Force generation of files, even if existing files are up-to-date')
        parser.add_argument(
            '--site-url',
            action='store',
            dest='site_url',
            default=None,
            help='Connect to a website other than %s' % settings.SITE_URL)

    def handle(self, *args, **options):
        # if no format was selected, select them all
        if not any([options[fmt] for fmt in self.formats]):
            for fmt in self.formats:
                options[fmt] = True
        generate(self.objdef, options)

    def _generate_downloads(self, activity, options):
        for fmt in self.formats:
            if options['all'] or options[fmt]:
                generate_one(self.objdef, fmt, activity, force=options['force'], site_url=options['site_url'])
