from datetime import date
from django.db.models import Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required

from .models import Household, Membership, Chore, ChoreCompletion
from .forms import HouseholdForm, JoinHouseholdForm, ChoreForm
from .rotation import current_responsible_index
from .periods import get_chore_status, get_period_delta
from .points import award_completion_points, award_verification_bonus
from .streaks import increment_streak


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


@login_required(login_url="/login/")
def board_view(request, pk):
    """Shared household board showing all chores, responsible member, and status."""
    household = get_object_or_404(Household, pk=pk)
    is_owner = household.owner == request.user
    is_member = is_owner or household.memberships.filter(user=request.user).exists()
    if not is_member:
        raise PermissionDenied("You are not a member of this household.")

    User = get_user_model()
    members_dict = {m.pk: m for m in household.get_members()}

    chore_rows = []
    today = date.today()
    for chore in household.chores.all().order_by("next_due_date"):
        responsible_member = None
        if chore.rotation_members:
            try:
                idx = current_responsible_index(
                    chore.rotation_members,
                    chore.next_due_date,
                    chore.frequency,
                    today,
                )
                member_pk = chore.rotation_members[idx]
                responsible_member = members_dict.get(member_pk) or User.objects.filter(pk=member_pk).first()
            except (ValueError, IndexError):
                responsible_member = None

        status = get_chore_status(chore, reference_date=today)
        can_complete = (
            request.user == responsible_member
            and status != "Done"
        )

        latest_completion = chore.completions.order_by("-completed_at").first()
        is_verified = latest_completion.verified if latest_completion else False

        if status == "Done":
            display_status = "Done ✓ (verified)" if is_verified else "Done (unverified)"
        else:
            display_status = status

        can_verify = (
            status == "Done"
            and latest_completion is not None
            and not is_verified
            and request.user != latest_completion.completed_by
        )

        chore_rows.append({
            "chore": chore,
            "responsible_member": responsible_member,
            "status": status,
            "display_status": display_status,
            "can_complete": can_complete,
            "can_verify": can_verify,
            "latest_completion": latest_completion,
        })

    return render(
        request,
        "chores/board.html",
        {
            "household": household,
            "chore_rows": chore_rows,
            "is_owner": is_owner,
        },
    )


@login_required(login_url="/login/")
def complete_chore(request, pk, chore_pk):
    """Mark a chore as complete. Assigned member only, POST only."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    household = get_object_or_404(Household, pk=pk)
    chore = get_object_or_404(Chore, pk=chore_pk, household=household)

    today = date.today()

    if not chore.rotation_members:
        raise PermissionDenied("Chore has no assigned rotation members.")

    idx = current_responsible_index(
        chore.rotation_members,
        chore.next_due_date,
        chore.frequency,
        today,
    )
    assigned_user_pk = chore.rotation_members[idx]
    if request.user.pk != assigned_user_pk:
        raise PermissionDenied("Only the currently assigned member can mark this chore complete.")

    if get_chore_status(chore, reference_date=today) == "Done":
        return HttpResponseBadRequest("Chore is already completed for this period.")

    completion = ChoreCompletion.objects.create(chore=chore, completed_by=request.user)
    award_completion_points(completion)
    increment_streak(completion)

    # Advance next_due_date by one period
    delta = get_period_delta(chore.frequency)
    chore.next_due_date += delta
    chore.save(update_fields=["next_due_date"])

    return redirect("chores:board", pk=household.pk)


@login_required(login_url="/login/")
def verify_completion(request, pk, completion_pk):
    """Verify a completed chore. Any household member except the completer."""
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    household = get_object_or_404(Household, pk=pk)
    is_owner = household.owner == request.user
    is_member = is_owner or household.memberships.filter(user=request.user).exists()
    if not is_member:
        raise PermissionDenied("You are not a member of this household.")

    completion = get_object_or_404(
        ChoreCompletion, pk=completion_pk, chore__household=household
    )

    if completion.completed_by == request.user:
        raise PermissionDenied("You cannot verify your own chore completion.")

    if not completion.verified:
        completion.verified = True
        completion.save(update_fields=["verified"])
        award_verification_bonus(completion)

    return redirect("chores:board", pk=household.pk)


@login_required(login_url="/login/")
def leaderboard_view(request, pk):
    """Ranked leaderboard of household members."""
    household = get_object_or_404(Household, pk=pk)
    is_owner = household.owner == request.user
    is_member = is_owner or household.memberships.filter(user=request.user).exists()
    if not is_member:
        raise PermissionDenied("You are not a member of this household.")

    # Ensure owner has a Membership record if not already created
    Membership.objects.get_or_create(household=household, user=household.owner)

    memberships = (
        Membership.objects
        .filter(household=household)
        .annotate(
            completed_chore_count=Count(
                "user__completions",
                filter=Q(user__completions__chore__household=household),
            )
        )
        .order_by("-points", "-completed_chore_count", "user__username")
        .select_related("user")
    )

    return render(
        request,
        "chores/leaderboard.html",
        {
            "household": household,
            "memberships": memberships,
        },
    )




