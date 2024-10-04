from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.core.exceptions import ValidationError

from .models import Recipe, RecipeImage

class RecipeForm(forms.ModelForm):
    """
    Form for creating and editing Recipe instances.
    Includes fields for basic recipe information and photo uploads.
    """
    photos = forms.FileField(required=False, label=_('Photos'))
    photos.widget.attrs['multiple'] = True

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients']
        labels = {
            'title': _('Title'),
            'description': _('Description'),
            'ingredients': _('Ingredients'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            'ingredients',
            'photos',
            Submit('submit', _('Save recipe'), css_class='btn-primary')
        )

    def clean_photos(self):
        photos = self.files.getlist('photos')
        for photo in photos:
            if photo.size > 10 * 1024 * 1024:  # 10 MB
                raise ValidationError(_('File is too large. Maximum size: 10 MB.'))
        return photos

    def save(self, commit=True):
        recipe = super().save(commit=False)
        if commit:
            recipe.save()

            # Processing photos
            for photo in self.files.getlist('photos'):
                RecipeImage.objects.create(recipe=recipe, image=photo)

        return recipe