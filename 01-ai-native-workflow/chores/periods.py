from datetime import date, timedelta


def get_period_delta(frequency: str) -> timedelta:
    if frequency == "weekly":
        return timedelta(weeks=1)
    return timedelta(days=1)


def get_period_window(next_due_date: date, frequency: str):
    delta = get_period_delta(frequency)
    return next_due_date, next_due_date + delta


def chore_has_completion_for_period(chore, period_start=None) -> bool:
    if not hasattr(chore, "completions"):
        return False
    if period_start is None:
        period_start = chore.next_due_date
    delta = get_period_delta(chore.frequency)
    start = period_start
    end = period_start + delta
    return chore.completions.filter(
        completed_at__date__gte=start,
        completed_at__date__lt=end,
    ).exists()


def get_chore_status(chore, reference_date=None) -> str:
    """
    Determine whether a chore is 'Done', 'Overdue', or 'Pending'.
    """
    if reference_date is None:
        reference_date = date.today()

    delta = get_period_delta(chore.frequency)

    if hasattr(chore, "completions"):
        latest = chore.completions.order_by("-completed_at").first()
        if latest:
            comp_date = latest.completed_at.date()
            prev_due = chore.next_due_date - delta
            if prev_due <= comp_date <= chore.next_due_date and reference_date < chore.next_due_date:
                return "Done"
            if comp_date == reference_date and chore.next_due_date > reference_date:
                return "Done"

    if chore.next_due_date < reference_date:
        return "Overdue"
    return "Pending"
