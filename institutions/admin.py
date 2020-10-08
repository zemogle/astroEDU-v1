from django.contrib import admin
from django import forms
from django.conf import settings
from parler.admin import TranslatableAdmin
# from sorl.thumbnail.admin import AdminImageMixin

from .models import Person, Institution, Location


# class InstitutionAdminForm(forms.ModelForm):
#     # class Meta:
#     #     model = Institution

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # the line below replaces     limit_choices_to={'folder__title': self.media_key()}
#         # in the model field definition. self isn't defined there, so this is the solution
#         self.fields['logo'].queryset = ManagedFile.objects.filter(folder__title=Institution().media_key())


@admin.register(Institution)
class InstitutionAdmin(TranslatableAdmin):  #, AdminImageMixin
    # form = InstitutionAdminForm

    def logo_embed(self, obj):
        if obj.logo:
            return '<img src="%s" style="height:50px" />' % obj.logo.image.icons['64']
    logo_embed.short_description = 'Logo'
    logo_embed.allow_tags = True

    list_display = ('name', 'fullname', 'url', 'location', 'all_languages_column', ) #'logo_embed', ) #'admin_logo', )
    list_editable = ('url', )
    ordering = ('name', )
    prepopulated_fields = {'slug': ('name', ), }


class PersonAdminForm(forms.ModelForm):

    class Meta:
        model = Person
        fields = ('name', 'citable_name', 'email', 'institution', 'spaceawe_partner', 'spaceawe_node', )

    def clean(self):
        cleaned_data = super().clean()

        institution = cleaned_data.get('institution')
        spaceawe_partner = cleaned_data.get('spaceawe_partner')
        spaceawe_node = cleaned_data.get('spaceawe_node')
        if (spaceawe_partner or spaceawe_node) and not institution:
            raise forms.ValidationError('Please fill in the institution (required for Space Awareness partners/nodes)')

        return cleaned_data


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    form = PersonAdminForm
    list_display = ('name', 'citable_name', 'email', 'institution', 'spaceawe_partner', 'spaceawe_node')
    list_editable = ('citable_name', 'email', 'spaceawe_partner', 'spaceawe_node', )


class LocationAdminForm(forms.ModelForm):

    class Meta:
        model = Location
        fields = ('city', 'country', 'latitude', 'longitude', )

    def clean_latitude(self):
        data = self.cleaned_data['latitude']
        if settings.SHORT_NAME == 'spaceawe':
            if not data:
                raise forms.ValidationError('Please fill in the latitude (required for Space Awareness partners/nodes)')
        return data

    def clean_longitude(self):
        data = self.cleaned_data['longitude']
        if settings.SHORT_NAME == 'spaceawe':
            if not data:
                raise forms.ValidationError('Please fill in the longitude (required for Space Awareness partners/nodes)')
        return data


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    form = LocationAdminForm
    list_display = ('city', 'country', 'latitude', 'longitude', )
