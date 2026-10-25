from chores.models import Membership


def award_completion_points(completion) -> int:
    """Award base points to the completing member. Returns points awarded."""
    membership = Membership.objects.filter(
        household=completion.chore.household,
        user=completion.completed_by,
    ).first()
    if membership:
        membership.points += completion.chore.point_value
        membership.save(update_fields=["points"])
        return completion.chore.point_value
    return 0


def award_verification_bonus(completion) -> int:
    """Award 10% floor bonus to the completing member. Returns bonus awarded."""
    bonus = completion.chore.point_value // 10
    membership = Membership.objects.filter(
        household=completion.chore.household,
        user=completion.completed_by,
    ).first()
    if membership:
        membership.points += bonus
        membership.save(update_fields=["points"])
        return bonus
    return 0
