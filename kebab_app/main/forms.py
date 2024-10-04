from django import forms
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import KebabSpot, Rating, KebabSpotPhoto, Comment, CommentPhoto, Complaint


class KebabSpotForm(forms.ModelForm):
    """
    Form for creating and editing KebabSpot instances.
    Includes fields for basic information, amenities, photos, and rating.
    """
    location = forms.CharField(widget=forms.HiddenInput())
    photos = forms.FileField(required=False)
    photos.widget.attrs['multiple'] = True
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
        labels = {
            'name': _('Name'),
            'description': _('Description'),
            'notes': _('Notes'),
            'payed_or_free': _('Paid or free'),
            'private_property': _('Private property'),
            'parking': _('Parking'),
            'toilets': _('Toilets'),
            'gazebos': _('Gazebos'),
            'tables': _('Tables'),
            'camping_places': _('Camping places'),
            'swimming_spot': _('Swimming spot'),
            'place_for_fire': _('Place for fire'),
            'trash_bins': _('Trash bins'),
        }

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
                _('Save'),
                css_class='btn btn-primary'
            )
        )

    def clean_location(self):
        """
        Validates and converts the location string to a Point object.
        """
        location = self.cleaned_data['location']
        if not location:
            raise ValidationError(_('You forgot to place a point on the map.'))
        try:
            lng, lat = map(float, location.split(','))
            return Point(lng, lat, srid=4326)
        except ValueError:
            raise ValidationError(_('Invalid point on the map.'))

    def clean_photos(self):
        """
        Validates the uploaded photos for quantity and size limits.
        """
        photos = self.files.getlist('photos')
        if len(photos) > 5:
            raise ValidationError(_('You can upload a maximum of 5 photos.'))
        for photo in photos:
            if photo.size > 10 * 1024 * 1024:  # 10 MB
                raise ValidationError(_('File is too large. Maximum size: 10 MB.'))
        return photos

    def save(self, commit=True, user=None):
        kebab_spot = super().save(commit=False)
        if commit:
            kebab_spot.save()

            # Processing photos
            for photo in self.files.getlist('photos'):
                KebabSpotPhoto.objects.create(kebab_spot=kebab_spot, image=photo)

            # Processing rating
            rating_value = self.cleaned_data.get('rating')
            if rating_value and user:
                Rating.objects.create(
                    user=user,
                    kebab_spot=kebab_spot,
                    value=rating_value
                )

        return kebab_spot


class KebabSpotFilterForm(forms.Form):
    """
    Form for filtering KebabSpot instances based on various criteria.
    """
    radius = forms.ChoiceField(
        label=_('Radius'),
        choices=[(10, _('10 km')), (20, _('20 km')), (30, _('30 km'))],
        initial=10,
        required=False
    )
    payed_or_free = forms.BooleanField(
        label=_('Paid'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    private_property = forms.BooleanField(
        label=_('Private property'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    parking = forms.BooleanField(
        label=_('Parking'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    toilets = forms.BooleanField(
        label=_('Toilets'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    gazebos = forms.BooleanField(
        label=_('Gazebos'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    tables = forms.BooleanField(
        label=_('Tables'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    camping_places = forms.BooleanField(
        label=_('Camping places'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    swimming_spot = forms.BooleanField(
        label=_('Swimming spot'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    place_for_fire = forms.BooleanField(
        label=_('Place for fire'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    trash_bins = forms.BooleanField(
        label=_('Trash bins'),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

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
            Submit('submit', _('Apply'), css_class='btn-primary full-width-btn')
        )


class CommentForm(forms.ModelForm):
    """
    Form for creating and editing comments on KebabSpot instances.
    Allows for text input and photo uploads.
    """
    class Meta:
        model = Comment
        fields = ['text']

    photos = forms.FileField(required=False, label=_('Photos'))
    photos.widget.attrs['multiple'] = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'text',
            'photos',
            Submit('submit', _('Save'), css_class='btn-primary')
        )

    def save(self, commit=True):
        comment = super().save(commit=False)
        if commit:
            comment.save()
            for photo in self.files.getlist('photos'):
                CommentPhoto.objects.create(comment=comment, image=photo)
        return comment


class ComplaintForm(forms.ModelForm):
    """
    Form for submitting complaints about KebabSpot instances.
    """
    class Meta:
        model = Complaint
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4, 'cols': 50})
        }
        labels = {
            'text': _('Reason for complaint')
        }
