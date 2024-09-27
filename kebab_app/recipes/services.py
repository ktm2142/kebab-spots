from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import JsonResponse

from main.mixins import RatingMixin
from .models import RecipeRating, Recipe


class RecipeService:
    def get_recipes(page_number, per_page=10):
        recipes = Recipe.objects.select_related('author').annotate(
            avg_rating=Avg('recipe_ratings__value')  # Додаємо рейтинг до кожного рецепта
        ).order_by('-created_at')
        paginator = Paginator(recipes, per_page)
        return paginator.get_page(page_number)


class RecipeSearchService:
    @staticmethod
    def search_recipes(query):
        if not query:
            return Recipe.objects.none()  # Повертає порожній queryset, якщо запит порожній

        return Recipe.objects.annotate(
            similarity=TrigramSimilarity('title', query) +
                       TrigramSimilarity('description', query) +
                       TrigramSimilarity('ingredients', query)
        ).filter(similarity__gt=0.1).order_by('-similarity')


class RecipeRatingService(RatingMixin):
    def __init__(self):
        super().__init__(RecipeRating, 'recipe')

    @classmethod
    def handle_post_request(cls, request, recipe):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return cls().handle_rating_update(request, recipe)
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)