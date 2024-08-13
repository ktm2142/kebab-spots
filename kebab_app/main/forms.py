from django import forms
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from .models import KebabSpot


class KebabSpotForm(forms.ModelForm):
    location = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = KebabSpot
        fields = ['name', 'description', 'location', 'notes', 'payed_or_free', 'private_property',
                  'parking', 'toilets', 'gazebos', 'tables', 'camping_places', 'swimming_spot',
                  'place_for_fire', 'trash_bins']

    def clean_location(self):
        location = self.cleaned_data['location']
        if not location:
            raise ValidationError('Ви забули поставити точку на карті.')
        try:
            lng, lat = map(float, location.split(','))
            return Point(lng, lat, srid=4326)
        except ValueError:
            raise ValidationError('Некоректна точка на карті.')



