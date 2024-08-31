from django.contrib import admin
from leaflet.admin import LeafletGeoAdmin
from .models import KebabSpot, KebabSpotPhoto

class KebabSpotPhotoInline(admin.TabularInline):
    model = KebabSpotPhoto
    extra = 0


@admin.register(KebabSpot)
class KebabSpotAdmin(LeafletGeoAdmin):
    list_display = ('id', 'name', 'created_by')
    readonly_fields = ('average_rating',)
    inlines = [KebabSpotPhotoInline]

