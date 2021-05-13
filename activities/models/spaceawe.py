from django.db import models
from django.utils.translation import ugettext_lazy as _


# SPACEAWE_CATEGORY_CHOICES = (
#     ('space', 'Space Exploration'),
#     ('planet', 'Earth Observation'),
#     ('nav', 'Navigation'),
#     ('herit', 'Islamic heritage'),
# )


SECTIONS = {
    'news': {
        'menu': _('News'),
        'title': _('News'),
        'subtitle': _('Latest updates about Space Awareness'),
        # 'teaser': _(''),
    },
    'careers': {
        'menu': _('Careers'),
        'title': _('Discover space careers'),
        'subtitle': _('Become a space explorer'),
        'teaser': _('Aiming for the stars? See how you can contribute to space science and exploration.'),
    },
    'scoops': {
        'menu': _('Read'),
        'title': _('Read Space Scoops'),
        'subtitle': _('News from across the Universe'),
        'teaser': _('The latest discoveries about the Universe.'),
    },
    'games': {
        'menu': _('Participate'),
        'title': _('Play & participate'),
        'subtitle': _('Apps and projects for space exploration'),
        'teaser': _('Some great apps and projects to take part in real research programmes.'),
    },
    'activities': {
        'menu': _('Educate'),
        'title': _('Educate & inspire'),
        'subtitle': _('Peer-reviewed educational activities'),
        'teaser': _('Some of the best resources for educators about space.'),
    },
    'skills': {
        'menu': _('Develop'),
        'title': _('Develop teaching skills'),
        'subtitle': _('Bringing space to education'),
        'teaser': _('Guidelines to best use Space Awareness with 8 to 18 year olds.'),
    },
    'about': {
        'menu': _('Know us'),
        'title': _('Get to know us'),
        'subtitle': _('Vision and team behind Space Awareness'),
        'teaser': _('Who is behind Space Awareness? Is there a contact in my country?'),
    },
}

CATEGORIES = {
    'space': {
        'filter_description': _('Space Exploration'),
        'title': _('Our wonderful Universe'),
        'subtitle': _('Space sciences and exploration'),
        'teaser': _('Get inspired by the beauty and vastness of the Universe'),
    },
    'earth': {
        'filter_description': _('Earth Observation'),
        'title': _('Our fragile planet'),
        'subtitle': _('Earth from above'),
        'teaser': _('The Earth, our unique and fragile home'),
    },
    'navigation': {
        'filter_description': _('Navigation'),
        'title': _('Navigation through the ages'),
        'subtitle': _('Global discovery & mobility'),
        'teaser': _('Trace the history of navigation from the first explorers to GPS'),
    },
    'heritage': {
        'filter_description': _('Islamic heritage'),
        'title': _('The journey of ideas'),
        'subtitle': _('Islamic heritage'),
        'teaser': _('Building a bridge between the Islamic world and Europe'),
    },
}


class SpaceaweModel(models.Model):
    space = models.BooleanField(default=False)
    earth = models.BooleanField(default=False)
    navigation = models.BooleanField(default=False)
    heritage = models.BooleanField(default=False)

    @property
    def spaceawe_categories(self):
        result = []
        if self.space:
            result.append({'code': 'space', 'title': CATEGORIES['space']['title'], })
        if self.earth:
            result.append({'code': 'earth', 'title': CATEGORIES['earth']['title'], })
        if self.navigation:
            result.append({'code': 'navigation', 'title': CATEGORIES['navigation']['title'], })
        if self.heritage:
            result.append({'code': 'heritage', 'title': CATEGORIES['heritage']['title'], })
        return result

    class Meta:
        abstract = True
