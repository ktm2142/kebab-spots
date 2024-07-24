from django.urls import path, include

from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('activation-sent/', views.ActivationSentView.as_view(), name='activation_sent'),
    path('activate/<str:token>/', views.ActivateView.as_view(), name='activate'),

    path('', include('allauth.urls')),

]
