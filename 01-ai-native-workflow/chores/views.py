from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .models import Household
from .forms import HouseholdForm


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
    """Dashboard — requires authentication."""
    household = Household.objects.filter(owner=request.user).first()
    return render(request, "chores/dashboard.html", {"user": request.user, "household": household})


@login_required(login_url="/login/")
def create_household(request):
    """Create a new household. Only one household allowed per owner."""
    if Household.objects.filter(owner=request.user).exists():
        existing = Household.objects.filter(owner=request.user).first()
        return render(
            request,
            "chores/household_form.html",
            {
                "error": "You already own a household.",
                "existing_household": existing,
            },
        )

    if request.method == "POST":
        form = HouseholdForm(request.POST)
        if form.is_valid():
            household = form.save(commit=False)
            household.owner = request.user
            household.save()
            return redirect("chores:household_detail", pk=household.pk)
    else:
        form = HouseholdForm()
    return render(request, "chores/household_form.html", {"form": form})


@login_required(login_url="/login/")
def household_detail(request, pk):
    """Display household details."""
    household = get_object_or_404(Household, pk=pk)
    return render(request, "chores/household_detail.html", {"household": household})
