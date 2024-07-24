from django.urls import path

from . import views

app_name = 'main'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('spot/<int:pk>/', views.KebabSpotDetailView.as_view(), name='spot_detail'),
]
