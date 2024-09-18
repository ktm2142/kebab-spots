from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import KebabSpot, KebabSpotPhoto, CommentPhoto, CommentRating, Comment, Complaint


class KebabSpotPhotoInline(admin.TabularInline):
    model = KebabSpotPhoto
    extra = 0


class ComplaintInline(admin.TabularInline):
    model = Complaint
    readonly_fields = ('user', 'text', 'created_at',)
    extra = 0

class CommentPhotoInline(admin.TabularInline):
    model = CommentPhoto
    extra = 0


class CommentRatingInline(admin.TabularInline):
    model = CommentRating
    extra = 0



@admin.register(KebabSpot)
class KebabSpotAdmin(LeafletGeoAdmin):
    list_display = ('id', 'name', 'created_by', 'complaints_count')
    readonly_fields = ('average_rating',)
    inlines = [KebabSpotPhotoInline, ComplaintInline]
    list_filter = ('created_by', 'hidden', 'complaints_count')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('kebab_spot', 'user', 'created_at')
    list_filter = ('kebab_spot', 'user', 'created_at')
    search_fields = ('text',)
    readonly_fields = ('kebab_spot', 'user', 'text', 'created_at',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('kebab_spot', 'user', 'text', 'created_at')
    list_filter = ('kebab_spot', 'user')
    search_fields = ('text',)
    inlines = [CommentPhotoInline, CommentRatingInline]
