from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout  # Import logout
from django.contrib.auth.decorators import login_required
from .forms import LoginForm


def login_view(request):
    """Handle user login"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')  # Or wherever you want to redirect after login
            else:
                form.add_error(None, "Invalid username or password")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def profile_view(request):
    """Display user profile information"""
    return render(request, 'accounts/profile.html')


def logout_view(request):
    """Handle user logout and redirect to login page"""
    logout(request)  # Log the user out
    return redirect('login')  # Redirect to the login view (named 'login' in urls.py)

