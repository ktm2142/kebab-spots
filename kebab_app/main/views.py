import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, DetailView, CreateView
from .forms import KebabSpotForm
from .mixins import NearbyKebabSpotsMixin, SearchKebabSpotsMixin
from .models import KebabSpot, KebabSpotPhoto, Rating
from .services import GeocodingService
from .forms import SearchForm

class HomeView(NearbyKebabSpotsMixin, TemplateView):
    template_name = 'home.html'

class SearchView(SearchKebabSpotsMixin, TemplateView):
    template_name = 'search.html'


class KebabSpotCreateView(LoginRequiredMixin, CreateView):
    model = KebabSpot
    form_class = KebabSpotForm
    template_name = 'create_kebab_spot.html'
    success_url = reverse_lazy('main:home')

    def get(self, request, *args, **kwargs):
        print("GET request received")  # Логування для перевірки
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        response = super().form_valid(form)
        for file in self.request.FILES.getlist('photos'):
            KebabSpotPhoto.objects.create(kebab_spot=self.object, image=file)

        rating_value = form.cleaned_data.get('rating')
        if rating_value:
            Rating.objects.create(
                user=self.request.user,
                kebab_spot=self.object,
                value=int(rating_value)
            )

        return response

class KebabSpotDetailView(DetailView):
    queryset = KebabSpot.objects.select_related('created_by').annotate(avg_rating=Avg('ratings__value'))
    template_name = 'kebab_spot_detail.html'
    context_object_name = 'spot'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['average_rating'] = self.object.avg_rating
        return context

    @method_decorator(login_required)
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            spot = self.get_object()
            rating_value = request.POST.get('rating')
            if rating_value:
                rating, created = Rating.objects.update_or_create(
                    user=request.user,
                    kebab_spot=spot,
                    defaults={'value': int(rating_value)}
                )
                return JsonResponse({
                    'status': 'success',
                    'avg_rating': spot.average_rating()
                })
        return JsonResponse({'status': 'error'}, status=400)


