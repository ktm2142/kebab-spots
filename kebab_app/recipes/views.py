from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, DetailView

from .forms import RecipeForm
from .models import Recipe
from .services import RecipeRatingService, RecipeService, RecipeSearchService


class RecipeListView(ListView):
    template_name = 'recipes_list.html'
    context_object_name = 'recipes'
    queryset = Recipe.objects.select_related('author').all()
    ordering = '-created_at'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_number = self.request.GET.get('page')
        context['recipes'] = RecipeService.get_recipes(page_number)
        return context


class RecipeDetailView(DetailView):
    queryset = Recipe.objects.select_related('author').annotate(avg_rating=Avg('recipe_ratings__value'))
    template_name = 'recipe_detail.html'
    context_object_name = 'recipe'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['average_rating'] = self.object.avg_rating or 0
        context['photos'] = self.object.recipe_images.all()
        return context

    @method_decorator(login_required)
    @method_decorator(require_POST)
    def post(self, request, *args, **kwargs):
        recipe = self.get_object()
        return RecipeRatingService.handle_post_request(request, recipe)


class CreateRecipeView(LoginRequiredMixin, CreateView):
    model = Recipe
    template_name = 'recipe_create.html'
    form_class = RecipeForm
    success_url = reverse_lazy('recipes:recipes_list')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class RecipeSearchView(ListView):
    model = Recipe
    template_name = 'recipe_search.html'
    context_object_name = 'recipes'
    paginate_by = 10  # Кількість результатів на сторінці

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        if not query:  # Якщо запит порожній, перенаправляємо на головну
            return redirect('recipes:recipes_list')
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        return RecipeSearchService.search_recipes(query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context