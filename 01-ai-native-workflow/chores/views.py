from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required


def index(request):
    """Placeholder home page."""
    return HttpResponse("<h1>Shared Household Chores</h1>")


def register_view(request):
    """Register a new user, auto-login, redirect to dashboard."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("chores:dashboard")
    else:
        form = UserCreationForm()
    return render(request, "chores/register.html", {"form": form})


def login_view(request):
    """Authenticate an existing user and redirect to dashboard (or ?next=)."""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get("next") or request.POST.get("next")
            return redirect(next_url if next_url else "chores:dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "chores/login.html", {"form": form})


def logout_view(request):
    """Log out the current user (POST only) and redirect to login."""
    if request.method == "POST":
        logout(request)
    return redirect("chores:login")


@login_required(login_url="/login/")
def dashboard_view(request):
    """Placeholder dashboard — requires authentication."""
    return render(request, "chores/dashboard.html", {"user": request.user})

