from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import KebabSpot, KebabSpotPhoto, CommentPhoto, CommentRating, Comment


class KebabSpotPhotoInline(admin.TabularInline):
    model = KebabSpotPhoto
    extra = 0


@admin.register(KebabSpot)
class KebabSpotAdmin(LeafletGeoAdmin):
    list_display = ('id', 'name', 'created_by')
    readonly_fields = ('average_rating',)
    inlines = [KebabSpotPhotoInline]


class CommentPhotoInline(admin.TabularInline):
    model = CommentPhoto
    extra = 0

class CommentRatingInline(admin.TabularInline):
    model = CommentRating
    extra = 0

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('kebab_spot', 'user', 'text', 'created_at')
    list_filter = ('kebab_spot', 'user')
    search_fields = ('text',)
    inlines = [CommentPhotoInline, CommentRatingInline]
