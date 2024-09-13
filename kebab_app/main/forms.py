from django import forms
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Field, HTML, Row, Column
from .models import KebabSpot, Rating, KebabSpotPhoto, Comment, CommentPhoto


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

    def save(self, commit=True, user=None):
        kebab_spot = super().save(commit=False)
        if commit:
            kebab_spot.save()

            # Обробка фотографій
            for photo in self.files.getlist('photos'):
                KebabSpotPhoto.objects.create(kebab_spot=kebab_spot, image=photo)

            # Обробка рейтингу
            rating_value = self.cleaned_data.get('rating')
            if rating_value and user:
                Rating.objects.create(
                    user=user,
                    kebab_spot=kebab_spot,
                    value=rating_value
                )

        return kebab_spot


class KebabSpotFilterForm(forms.Form):
    radius = forms.ChoiceField(label='Радіус', choices=[(10, '10 км'), (20, '20 км'), (30, '30 км')], initial=10,
                               required=False)
    payed_or_free = forms.BooleanField(label='Платно', required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    private_property = forms.BooleanField(label='Приватна територія', required=False,
                                          widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    parking = forms.BooleanField(label='Парковка', required=False,
                                 widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    toilets = forms.BooleanField(label='Туалети', required=False,
                                 widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    gazebos = forms.BooleanField(label='Альтанки', required=False,
                                 widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    tables = forms.BooleanField(label='Столи', required=False,
                                widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    camping_places = forms.BooleanField(label='Місця для кемпінгу', required=False,
                                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    swimming_spot = forms.BooleanField(label='Місце для купання', required=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    place_for_fire = forms.BooleanField(label='Місце для вогнища', required=False,
                                        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    trash_bins = forms.BooleanField(label='Смітники', required=False,
                                    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.layout = Layout(
            'radius',
            Row(
                Column('payed_or_free', css_class='form-group col-md-6 mb-0'),
                Column('private_property', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('parking', css_class='form-group col-md-6 mb-0'),
                Column('toilets', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('gazebos', css_class='form-group col-md-6 mb-0'),
                Column('tables', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('camping_places', css_class='form-group col-md-6 mb-0'),
                Column('swimming_spot', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('place_for_fire', css_class='form-group col-md-6 mb-0'),
                Column('trash_bins', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Застосувати фільтри', css_class='btn-primary')
        )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

    photos = forms.FileField(required=False)
    photos.widget.attrs['multiple'] = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'text',
            'photos',  # Додати поле для завантаження фото
            Submit('submit', 'Зберегти', css_class='btn-primary')
        )

    def save(self, commit=True):
        comment = super().save(commit=False)
        if commit:
            comment.save()
            for photo in self.files.getlist('photos'):
                CommentPhoto.objects.create(comment=comment, image=photo)
        return comment