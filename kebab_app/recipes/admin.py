from django.contrib import admin

from .models import Recipe, RecipeImage


class RecipeImageInline(admin.TabularInline):
    model = RecipeImage
    extra = 0

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'created_at')
    list_filter = ('author', 'created_at')
    inlines = [RecipeImageInline]
    search_fields = ('name',)



