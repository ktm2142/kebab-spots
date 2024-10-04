from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from django.views.generic import ListView
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import redirect
from django.urls import reverse
from main.models import KebabSpot
from recipes.models import Recipe


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get(self, request, *args, **kwargs):
        if 'google' in request.GET:
            return redirect(reverse('google_login'))  # Змінено на 'google_login'
        return super().get(request, *args, **kwargs)

class CustomLogoutView(LogoutView):
    next_page = settings.LOGOUT_REDIRECT_URL


class UserKebabSpotsView(LoginRequiredMixin, ListView):
    template_name = 'accounts/user_kebab_spots.html'
    context_object_name = 'kebab_spots'
    queryset = (KebabSpot.objects
                .select_related('created_by')
                .annotate(
                    comments_count=Count('comments'),
                    avg_rating=Avg('ratings__value'))
                .order_by('-created_at')
                )


class UserRecipesView(LoginRequiredMixin, ListView):
    template_name = 'accounts/user_recipes.html'
    context_object_name = 'recipes'
    queryset = (Recipe.objects
                .select_related('author')
                .annotate(
                    avg_rating=Avg('recipe_ratings__value'))
                .order_by('-created_at')
                )
