from django import forms
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML
from .models import KebabSpot, Rating


class KebabSpotForm(forms.ModelForm):
    location = forms.CharField(widget=forms.HiddenInput())
    photos = forms.FileField(required=False)
    photos.widget.attrs['multiple'] = True
    help_text = 'Оберіть одну або декілька фотографій. Дозволені формати: jpg, jpeg, png.'
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        required=False,
        min_value=1,
        max_value=5
    )

    class Meta:
        model = KebabSpot
        fields = ['name', 'description', 'location', 'notes', 'payed_or_free', 'private_property',
                  'parking', 'toilets', 'gazebos', 'tables', 'camping_places', 'swimming_spot',
                  'place_for_fire', 'trash_bins', 'rating']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            'location',
            'notes',
            'payed_or_free',
            'private_property',
            'parking',
            'toilets',
            'gazebos',
            'tables',
            'camping_places',
            'swimming_spot',
            'place_for_fire',
            'trash_bins',
            'photos',
            'rating',
            Submit(
                'submit',
                'Зберегти',
                css_class='btn btn-primary'
            )
        )


    def clean_location(self):
        location = self.cleaned_data['location']
        if not location:
            raise ValidationError('Ви забули поставити точку на карті.')
        try:
            lng, lat = map(float, location.split(','))
            return Point(lng, lat, srid=4326)
        except ValueError:
            raise ValidationError('Некоректна точка на карті.')

    def clean_photos(self):
        photos = self.files.getlist('photos')
        for photo in photos:
            if photo.size > 10 * 1024 * 1024:  # 10 MB
                raise ValidationError('Файл занадто великий. Максимальний розмір: 10 MB.')
        return photos

