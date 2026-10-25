from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed
from django.core.exceptions import PermissionDenied
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .models import Household, Membership, Chore
from .forms import HouseholdForm, JoinHouseholdForm, ChoreForm


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
    if not household:
        membership = Membership.objects.filter(user=request.user).select_related("household").first()
        if membership:
            household = membership.household
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
            Membership.objects.create(household=household, user=request.user)
            return redirect("chores:household_detail", pk=household.pk)
    else:
        form = HouseholdForm()
    return render(request, "chores/household_form.html", {"form": form})


@login_required(login_url="/login/")
def household_detail(request, pk):
    """Display household details and members."""
    household = get_object_or_404(Household, pk=pk)
    members = household.get_members()
    return render(request, "chores/household_detail.html", {"household": household, "members": members})


@login_required(login_url="/login/")
def join_household(request):
    """Join an existing household using an invite code."""
    if request.method == "POST":
        form = JoinHouseholdForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["invite_code"].strip()
            try:
                household = Household.objects.get(invite_code=code)
            except Household.DoesNotExist:
                return render(
                    request,
                    "chores/join_household.html",
                    {"form": form, "error": "Invalid invite code."},
                )

            # Check if user is already a member of this household
            if (
                household.owner == request.user
                or Membership.objects.filter(household=household, user=request.user).exists()
            ):
                return render(
                    request,
                    "chores/join_household.html",
                    {"form": form, "error": "You are already a member of this household."},
                )

            # Check if user belongs to another household
            in_other_household = (
                Household.objects.filter(owner=request.user).exclude(pk=household.pk).exists()
                or Membership.objects.filter(user=request.user).exclude(household=household).exists()
            )
            if in_other_household:
                return render(
                    request,
                    "chores/join_household.html",
                    {"form": form, "error": "You already belong to another household."},
                )

            Membership.objects.create(household=household, user=request.user)
            return redirect("chores:household_detail", pk=household.pk)
    else:
        form = JoinHouseholdForm()

    return render(request, "chores/join_household.html", {"form": form})


@login_required(login_url="/login/")
def chore_list(request, pk):
    """List all chores for a household. Members only."""
    household = get_object_or_404(Household, pk=pk)
    is_owner = household.owner == request.user
    is_member = is_owner or household.memberships.filter(user=request.user).exists()
    if not is_member:
        raise PermissionDenied("You are not a member of this household.")

    chores = household.chores.all().order_by("next_due_date")
    return render(
        request,
        "chores/chore_list.html",
        {
            "household": household,
            "chores": chores,
            "is_owner": is_owner,
        },
    )


@login_required(login_url="/login/")
def chore_create(request, pk):
    """Create a new chore. Owner only."""
    household = get_object_or_404(Household, pk=pk)
    if household.owner != request.user:
        raise PermissionDenied("Only the household owner can create chores.")

    if request.method == "POST":
        form = ChoreForm(request.POST, household=household)
        if form.is_valid():
            chore = form.save(commit=False)
            chore.household = household
            chore.save()
            return redirect("chores:chore_list", pk=household.pk)
    else:
        form = ChoreForm(household=household)

    return render(
        request,
        "chores/chore_form.html",
        {"household": household, "form": form, "action": "Create"},
    )


@login_required(login_url="/login/")
def chore_edit(request, pk, chore_pk):
    """Edit an existing chore. Owner only."""
    household = get_object_or_404(Household, pk=pk)
    if household.owner != request.user:
        raise PermissionDenied("Only the household owner can edit chores.")
    chore = get_object_or_404(Chore, pk=chore_pk, household=household)

    if request.method == "POST":
        form = ChoreForm(request.POST, instance=chore, household=household)
        if form.is_valid():
            form.save()
            return redirect("chores:chore_list", pk=household.pk)
    else:
        form = ChoreForm(instance=chore, household=household)

    return render(
        request,
        "chores/chore_form.html",
        {"household": household, "chore": chore, "form": form, "action": "Edit"},
    )


@login_required(login_url="/login/")
def chore_delete(request, pk, chore_pk):
    """Delete a chore. Owner only, POST only."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    household = get_object_or_404(Household, pk=pk)
    if household.owner != request.user:
        raise PermissionDenied("Only the household owner can delete chores.")
    chore = get_object_or_404(Chore, pk=chore_pk, household=household)
    chore.delete()
    return redirect("chores:chore_list", pk=household.pk)
