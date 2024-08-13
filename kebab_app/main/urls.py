from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


app_name = 'main'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('create-kebab-spot', views.KebabSpotCreateView.as_view(), name='create_kebab_spot'),
    path('spot/<int:pk>/', views.KebabSpotDetailView.as_view(), name='kebab_spot_detail'),
]
