from django.http import JsonResponse
from django.core.serializers import serialize
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from .models import KebabSpot

class NearbyKebabSpotsMixin:
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            lat = request.GET.get('lat')
            lng = request.GET.get('lng')
            if lat and lng:
                user_location = Point(float(lng), float(lat), srid=4326)
                kebab_spots = KebabSpot.objects.annotate(
                    distance=Distance('location', user_location)
                ).filter(distance__lte=D(km=10))
                return JsonResponse(serialize('json', kebab_spots, fields=('name', 'location')), safe=False)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        kebab_spots = KebabSpot.objects.all()
        context['kebab_spots_json'] = serialize('json', kebab_spots, fields=('name', 'location'))
        return context
