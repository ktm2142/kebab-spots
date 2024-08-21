from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import TemplateView, DetailView, CreateView
from .forms import KebabSpotForm
from .mixin import NearbyKebabSpotsMixin
from .models import KebabSpot, KebabSpotPhoto, Rating


class HomeView(NearbyKebabSpotsMixin, TemplateView):
    template_name = 'home.html'


class KebabSpotCreateView(LoginRequiredMixin, NearbyKebabSpotsMixin, CreateView):
    model = KebabSpot
    form_class = KebabSpotForm
    template_name = 'create_kebab_spot.html'
    success_url = reverse_lazy('main:home')

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
    model = KebabSpot
    template_name = 'kebab_spot_detail.html'
    context_object_name = 'spot'



