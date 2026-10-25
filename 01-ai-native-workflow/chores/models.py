import secrets
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


class Household(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_households",
    )
    invite_code = models.CharField(max_length=32, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = secrets.token_urlsafe(8)
        super().save(*args, **kwargs)

    def get_members(self):
        """Return all members of the household, always including the owner."""
        member_ids = set(self.memberships.values_list("user_id", flat=True))
        member_ids.add(self.owner_id)
        return get_user_model().objects.filter(id__in=member_ids)

    def __str__(self):
        return self.name


class Membership(models.Model):
    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    points = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [("household", "user")]

    def __str__(self):
        return f"{self.user.username} in {self.household.name}"


class Chore(models.Model):
    class Frequency(models.TextChoices):
        DAILY = "daily", "Daily"
        WEEKLY = "weekly", "Weekly"

    household = models.ForeignKey(
        Household,
        on_delete=models.CASCADE,
        related_name="chores",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    frequency = models.CharField(
        max_length=10,
        choices=Frequency.choices,
    )
    point_value = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    rotation_members = models.JSONField(default=list, blank=True)
    next_due_date = models.DateField()

    def __str__(self):
        return f"{self.title} ({self.household.name})"


class ChoreCompletion(models.Model):
    chore = models.ForeignKey(
        Chore,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="completions",
    )
    completed_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.chore.title} completed by {self.completed_by.username} at {self.completed_at}"

