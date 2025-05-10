"""
URL configuration for familytree_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf.urls.i18n import i18n_patterns
from inventory.views import dashboard, change_language

# Special URL patterns that don't need i18n (not language specific)
urlpatterns = [
    path('change-language/', change_language, name='change_language'),
    path('i18n/', include('django.conf.urls.i18n')),  # Django's built-in translation interface
]

# URL patterns that should use language prefix (e.g., /en/dashboard/, /ar/dashboard/)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('inventory/', include('inventory.urls', namespace='inventory')),
    path('dashboard/', dashboard, name='dashboard'),
    path('', RedirectView.as_view(url='dashboard/')),
    prefix_default_language=True  # Include prefix for default language
)
