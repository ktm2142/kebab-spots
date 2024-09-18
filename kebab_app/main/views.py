from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import Avg, Prefetch, Count, Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, DetailView, CreateView
from .forms import KebabSpotForm, KebabSpotFilterForm, CommentForm, ComplaintForm

from .models import KebabSpot, KebabSpotPhoto, Rating, Comment, CommentPhoto, CommentRating, Complaint
from .services import KebabSpotRatingService, CommentService, NearbyKebabSpotsService, SearchKebabSpotsService


class HomeView(NearbyKebabSpotsService, TemplateView):
    template_name = 'home.html'


class SearchView(SearchKebabSpotsService, TemplateView):
    template_name = 'search.html'


class KebabSpotCreateView(LoginRequiredMixin, CreateView):
    model = KebabSpot
    form_class = KebabSpotForm
    template_name = 'create_kebab_spot.html'
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        self.object = form.save(user=self.request.user)
        return HttpResponseRedirect(self.get_success_url())


class KebabSpotDetailView(DetailView):
    queryset = KebabSpot.objects.select_related('created_by').annotate(avg_rating=Avg('ratings__value'))
    template_name = 'kebab_spot_detail.html'
    context_object_name = 'spot'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['average_rating'] = self.object.avg_rating
        page_number = self.request.GET.get('page')
        context['comments'] = CommentService.get_paginated_comments(self.object, page_number)
        context['form'] = kwargs.get('form', CommentForm())
        return context

    @method_decorator(login_required)
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        spot = self.get_object()
        if CommentService.delete_comment_request(request):
            return redirect(request.path)  # Перенаправлення на ту ж сторінку
        return KebabSpotRatingService.handle_post_request(self, request, spot)

    def handle_comment_form(self, request, spot):
        success, result = CommentService.create_comment(request.user, spot, request.POST, request.FILES)
        if success:
            return redirect(reverse('main:kebab_spot_detail', kwargs={'pk': spot.pk}))

        context = self.get_context_data(object=spot, form=result)
        return self.render_to_response(context)


class KebabComplaintView(LoginRequiredMixin, CreateView):
    model = Complaint
    form_class = ComplaintForm
    template_name = 'submit_complaint.html'
    success_url = reverse_lazy('main:home')

    def form_valid(self, form):
        kebab_spot_id = self.kwargs['pk']
        kebab_spot = get_object_or_404(KebabSpot, pk=kebab_spot_id)

        try:
            with transaction.atomic():
                complaint = form.save(commit=False)
                complaint.kebab_spot = kebab_spot
                complaint.user = self.request.user
                complaint.save()

                # Збільшуємо кількість скарг
                kebab_spot.complaints_count += 1

                # Перевіряємо, чи потрібно приховати точку
                if kebab_spot.complaints_count >= 5:
                    kebab_spot.hidden = True

                kebab_spot.save()

                if kebab_spot.hidden:
                    messages.warning(self.request,
                                     'Точку відправлено на розгляд та приховано через велику кількість скарг.')
                else:
                    messages.success(self.request, 'Вашу скаргу було подано.')

        except IntegrityError:
            messages.error(self.request, 'Ви вже подавали скаргу на цю точку.')
            return self.form_invalid(form)

        return super().form_valid(form)
