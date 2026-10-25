from chores.models import Membership
from chores.rotation import current_responsible_index


def increment_streak(completion) -> int:
    """Increment current_streak for the member completing their assigned chore."""
    membership = Membership.objects.filter(
        household=completion.chore.household,
        user=completion.completed_by,
    ).first()
    if membership:
        membership.current_streak += 1
        membership.save(update_fields=["current_streak"])
        return membership.current_streak
    return 0


def reset_streak_for_overdue_chore(chore) -> None:
    """Reset current_streak to 0 for the assigned member of an overdue chore."""
    if not chore.rotation_members:
        return
    idx = current_responsible_index(
        chore.rotation_members,
        chore.next_due_date,
        chore.frequency,
        chore.next_due_date,
    )
    assigned_user_pk = chore.rotation_members[idx]
    membership = Membership.objects.filter(
        household=chore.household,
        user_id=assigned_user_pk,
    ).first()
    if membership:
        membership.current_streak = 0
        membership.save(update_fields=["current_streak"])
