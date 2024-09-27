from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django.core.exceptions import ValidationError

from .models import Recipe, RecipeImage


class RecipeForm(forms.ModelForm):
    photos = forms.FileField(required=False)
    photos.widget.attrs['multiple'] = True

    class Meta:
        model = Recipe
        fields = ['title', 'description', 'ingredients']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'description',
            'ingredients',
            'photos',  # Додаємо поле для завантаження фото
            Submit('submit', 'Зберегти рецепт', css_class='btn-primary')
        )

    def clean_photos(self):
        photos = self.files.getlist('photos')
        for photo in photos:
            if photo.size > 10 * 1024 * 1024:  # 10 MB
                raise ValidationError('Файл занадто великий. Максимальний розмір: 10 MB.')
        return photos

    def save(self, commit=True):
        recipe = super().save(commit=False)
        if commit:
            recipe.save()

            # Обробка фотографій
            for photo in self.files.getlist('photos'):
                RecipeImage.objects.create(recipe=recipe, image=photo)

        return recipe
