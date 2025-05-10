from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page=reverse_lazy('accounts:login')), name='logout'),
    path('profile/', views.profile_view, name='profile'),
]

