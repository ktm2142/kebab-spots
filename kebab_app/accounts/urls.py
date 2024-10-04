from django.urls import path, include

from . import views


app_name = 'accounts'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('user_spots/', views.UserKebabSpotsView.as_view(), name='user_kebab_spots'),
    path('user_recipes/', views.UserRecipesView.as_view(), name='user_recipes'),
    path('', include('allauth.urls')),

]
