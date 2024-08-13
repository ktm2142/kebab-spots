from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView
from .forms import KebabSpotForm
from .mixin import NearbyKebabSpotsMixin
from .models import KebabSpot, KebabSpotPhoto


class HomeView(NearbyKebabSpotsMixin, TemplateView):
    template_name = 'home.html'


class KebabSpotCreateView(LoginRequiredMixin, NearbyKebabSpotsMixin, CreateView):
    model = KebabSpot
    form_class = KebabSpotForm
    template_name = 'create_kebab_spot.html'
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class KebabSpotDetailView(DetailView):
    model = KebabSpot
    template_name = 'kebab_spot_detail.html'
    context_object_name = 'spot'



