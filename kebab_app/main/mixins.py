from django.db.models import Avg
from django.http import JsonResponse
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.urls import reverse

from .models import KebabSpot
from .services import GeocodingService


from django.db.models import Avg
from django.http import JsonResponse, HttpResponse
from django.core.serializers import serialize
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D
from django.urls import reverse

from .models import KebabSpot

class NearbyKebabSpotsMixin:
    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            lat = request.GET.get('lat')
            lng = request.GET.get('lng')
            if lat and lng:
                user_location = Point(float(lng), float(lat), srid=4326)
                kebab_spots = KebabSpot.objects.annotate(
                    distance=Distance('location', user_location),
                    avg_rating=Avg('ratings__value')
                ).filter(distance__lte=D(km=10))
                spots_data = [{
                    'id': spot.id,
                    'name': spot.name,
                    'lat': spot.location.y,
                    'lng': spot.location.x,
                    'url': reverse('main:kebab_spot_detail', args=[spot.id]),
                    'avg_rating': round(spot.avg_rating, 1) if spot.avg_rating else 0
                } for spot in kebab_spots]
                return JsonResponse(spots_data, safe=False)
            else:
                return JsonResponse({'error': 'Геолокація не надана'}, status=400)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kebab_spots_json'] = []
        return context


class SearchKebabSpotsMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q')

        if query:
            geocoding_service = GeocodingService()
            coordinates = geocoding_service.get_coordinates(query)
            if coordinates:
                location = Point(coordinates[1], coordinates[0], srid=4326)
                kebab_spots = KebabSpot.objects.annotate(
                    distance=Distance('location', location),
                    avg_rating=Avg('ratings__value')
                ).filter(distance__lte=D(km=10))

                # Додаємо координати пошуку до контексту
                context['search_coordinates'] = {
                    'lat': coordinates[0],
                    'lng': coordinates[1]
                }
            else:
                kebab_spots = KebabSpot.objects.none()
        else:
            kebab_spots = KebabSpot.objects.annotate(avg_rating=Avg('ratings__value'))

        context['kebab_spots_json'] = [{
            'id': spot.id,
            'name': spot.name,
            'lat': spot.location.y,
            'lng': spot.location.x,
            'url': reverse('main:kebab_spot_detail', args=[spot.id]),
            'avg_rating': round(spot.avg_rating, 1) if spot.avg_rating else 0
        } for spot in kebab_spots]

        context['query'] = query
        return context


# class SearchKebabSpotsMixin:
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         query = self.request.GET.get('q')
#         if query:
#             geocoding_service = GeocodingService()
#             coordinates = geocoding_service.get_coordinates(query)
#             if coordinates:
#                 location = Point(coordinates[1], coordinates[0], srid=4326)
#                 kebab_spots = KebabSpot.objects.annotate(
#                     distance=Distance('location', location),
#                     avg_rating=Avg('ratings__value')
#                 ).filter(distance__lte=D(km=10))
#             else:
#                 kebab_spots = KebabSpot.objects.none()
#         else:
#             kebab_spots = KebabSpot.objects.annotate(avg_rating=Avg('ratings__value'))
#         context['kebab_spots_json'] = [{
#             'id': spot.id,
#             'name': spot.name,
#             'lat': spot.location.y,
#             'lng': spot.location.x,
#             'url': reverse('main:kebab_spot_detail', args=[spot.id]),
#             'avg_rating': round(spot.avg_rating, 1) if spot.avg_rating else 0
#         } for spot in kebab_spots]
#
#         context['query'] = query
#         return context
