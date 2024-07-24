from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
from rest_framework.response import Response

from .models import KebabSpot
from .serializers import KebabSpotSerializer


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_nearby_spots(self, request):
        lat = float(request.GET.get('lat', 0))
        lon = float(request.GET.get('lon', 0))
        radius = float(request.GET.get('radius', 10))

        user_location = Point(lon, lat, srid=4326)
        nearby_spots = KebabSpot.objects.filter(
            location__distance_lte=(user_location, D(km=radius))
        )

        serializer = KebabSpotSerializer(nearby_spots, many=True)
        return Response(serializer.data)


class KebabSpotDetailView(DetailView):
    model = KebabSpot
    template_name = 'kebab_spot_detail.html'
    context_object_name = 'spot'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     return context
