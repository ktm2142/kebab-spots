from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Avg
from django.views.generic import CreateView, TemplateView, ListView
from django.contrib.auth import login
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.core.mail import send_mail
from .forms import RegistrationForm
from .models import ActivationToken
from main.models import KebabSpot


class RegisterView(CreateView):
    form_class = RegistrationForm
    success_url = reverse_lazy('home')
    template_name = 'accounts/user_create.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        user = self.object
        user.is_active = False
        user.save()

        token = ActivationToken.create(user)
        activation_link = self.request.build_absolute_uri(
            reverse_lazy('accounts:activate', kwargs={'token': token.token})
        )
        send_mail(
            'Активація аккаунту',
            f'Для активації аккаунту перейдіть за посиланням: {activation_link}',
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return response


class ActivationSentView(TemplateView):
    template_name = 'accounts/activation_sent.html'


class ActivateView(TemplateView):
    template_name = 'accounts/activation_complete.html'

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        try:
            activation_token = get_object_or_404(ActivationToken, token=token)
            user = activation_token.user
            if user.is_active:
                return render(request, 'accounts/activation_already_done.html')

            if not activation_token.is_valid():
                return render(request, 'accounts/activation_invalid.html')

            user.is_active = True
            user.save()
            activation_token.delete()
            login(request, user)
            return super().get(request, *args, **kwargs)
        except ActivationToken.DoesNotExist:
            return render(request, 'accounts/activation_invalid.html')


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'


class CustomLogoutView(LogoutView):
    next_page = settings.LOGOUT_REDIRECT_URL


class UserProfileView(LoginRequiredMixin, ListView):
    template_name = 'accounts/user_profile.html'
    context_object_name = 'kebab_spots'
    queryset = (KebabSpot.objects
                .select_related('created_by')
                .annotate(
                    comments_count=Count('comments'),
                    avg_rating=Avg('ratings__value'))
                .order_by('-created_at')
                )

