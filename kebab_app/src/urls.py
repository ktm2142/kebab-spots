from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('accounts/', include('allauth.urls')),
]

# Додайте URL-шаблони, які ви хочете локалізувати, до i18n_patterns
urlpatterns += i18n_patterns(
    path('', include('main.urls', namespace='main')),
    path('recipes/', include('recipes.urls', namespace='recipes')),
)

# Додайте статичні та медіа URL-шаблони
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns