from django.urls import path, include

from . import views

app_name = 'recipes'

urlpatterns = [
    path('', views.RecipeListView.as_view(), name='recipes_list'),
    path('create/', views.CreateRecipeView.as_view(), name='create_recipe'),
    path('<int:pk>/', views.RecipeDetailView.as_view(), name='recipe_detail'),
    path('search/', views.RecipeSearchView.as_view(), name='recipe_search'),
]
