from datetime import date
from typing import Literal

Frequency = Literal["daily", "weekly"]


def current_responsible_index(
    rotation_members: list[int],
    next_due_date: date,
    frequency: str,
    reference_date: date,
) -> int:
    """
    Return the index into `rotation_members` of the member currently
    responsible for the chore.

    Parameters
    ----------
    rotation_members : list of user PKs in rotation order (length >= 1)
    next_due_date    : the date the chore is next due
    frequency        : "daily" or "weekly"
    reference_date   : the date to evaluate against (typically date.today())

    Returns
    -------
    int : 0-based index into rotation_members

    Raises
    ------
    ValueError : if rotation_members is empty or frequency is invalid
    """
    if not rotation_members:
        raise ValueError("rotation_members cannot be empty")

    if frequency == "daily":
        period_days = 1
    elif frequency == "weekly":
        period_days = 7
    else:
        raise ValueError(f"Unsupported frequency: {frequency}")

    if reference_date < next_due_date:
        return 0

    delta_days = (reference_date - next_due_date).days
    periods_elapsed = delta_days // period_days

    return periods_elapsed % len(rotation_members)
