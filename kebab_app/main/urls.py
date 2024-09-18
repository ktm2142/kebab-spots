from django.urls import path
from django.urls import path, include
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('create-kebab-spot', views.KebabSpotCreateView.as_view(), name='create_kebab_spot'),
    path('kebab-spot/<int:pk>/', views.KebabSpotDetailView.as_view(), name='kebab_spot_detail'),
    path('search', views.SearchView.as_view(), name='search'),
    path('kebab-complaint/<int:pk>/', views.KebabComplaintView.as_view(), name='submit_complaint'),
]
