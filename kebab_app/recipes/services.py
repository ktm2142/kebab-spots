from django.contrib.postgres.search import TrigramSimilarity
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from main.mixins import RatingMixin
from .models import RecipeRating, Recipe


class RecipeService:
    """
    Service class for handling recipe-related operations.
    """

    @staticmethod
    def get_recipes(page_number, per_page=10):
        """
        Retrieves a paginated list of recipes with their average ratings.
        Args:
            page_number (int): The page number to retrieve.
            per_page (int): The number of recipes per page. Defaults to 10.
        Returns:
            Page: A page object containing the requested recipes.
        """
        recipes = Recipe.objects.select_related('author').annotate(
            avg_rating=Avg('recipe_ratings__value')
        ).order_by('-created_at')
        paginator = Paginator(recipes, per_page)
        return paginator.get_page(page_number)


class RecipeSearchService:
    """
    Service class for searching recipes.
    """

    @staticmethod
    def search_recipes(query):
        """
        Searches for recipes based on a given query using trigram similarity.
        Args:
            query (str): The search query.
        Returns:
            QuerySet: A queryset of Recipe objects matching the search criteria,
                      ordered by similarity to the query.
        """
        if not query:
            return Recipe.objects.none()

        return Recipe.objects.annotate(
            similarity=TrigramSimilarity('title', query) +
                       TrigramSimilarity('description', query) +
                       TrigramSimilarity('ingredients', query)
        ).filter(similarity__gt=0.1).order_by('-similarity')


class RecipeRatingService(RatingMixin):
    """
    Service class for handling recipe ratings.
    Inherits from RatingMixin to provide common rating functionality.
    """

    def __init__(self):
        super().__init__(RecipeRating, 'recipe')

    @classmethod
    def handle_post_request(cls, request, recipe):
        """
        Handles POST requests for updating recipe ratings.
        Args:
            request (HttpRequest): The HTTP request object.
            recipe (Recipe): The recipe object being rated.
        Returns:
            JsonResponse: A JSON response indicating the status of the rating update.
        """
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return cls().handle_rating_update(request, recipe)
        return JsonResponse({'status': 'error', 'message': _('Invalid request')}, status=400)