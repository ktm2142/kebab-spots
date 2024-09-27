from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
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
from .services import KebabSpotRatingService, CommentService, NearbyKebabSpotsService, SearchKebabSpotsService, \
    ComplaintService


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
        success, error_message = ComplaintService.submit_complaint(self.request, kebab_spot_id, form)

        if success:
            return super().form_valid(form)
        else:
            messages.error(self.request, error_message)
            return self.form_invalid(form)
