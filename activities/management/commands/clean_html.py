import re

from django.core.management.base import BaseCommand, CommandError

from activities.models import Activity
from activities.models import ACTIVITY_SECTIONS

class Command(BaseCommand):
    help = 'translates some html on markdown to proper markdown'

    def handle(self, *args, **options):
        for activity in Activity.objects.all():
            self.stdout.write('Activity "%s"... ' % activity.code)
            dirty = False
            for section_code, section_title in ACTIVITY_SECTIONS:
                text = getattr(activity, section_code)
                text_out = text

                # replace <a href=...
                new_start = 0
                text_out2 = ''
                for m in re.finditer(ur'<a href="(.*?)" target="_blank">(.*?)</a>', text_out):
                    if m.group(1) == m.group(2):
                        new_link = m.group(2)
                    else:
                        new_link = m.expand(ur'[\2](\1)')
                    text_out2 += text_out[new_start:m.start()] + new_link
                    new_start = m.end()
                text_out = text_out2 + text_out[new_start:]

                # for m in re.finditer(ur'<a href', text_out):
                #     print(m.group(0))

                # replace weird <it>...
                text_out = re.sub(ur'<it>(.*?)</it>', ur'_\1_', text_out)

                # replace <br> with <br/>...
                text_out = re.sub(ur'<br>', ur'<br/>', text_out)

                # replace badly nested lists
                text_out = re.sub(ur'^-- ', ur'    - ', text_out, flags=re.MULTILINE)

                if text_out != text:
                    dirty = True
                    print(section_code)
                    setattr(activity, section_code, text_out)

            if dirty:
                activity.save()
            self.stdout.write('done.')

