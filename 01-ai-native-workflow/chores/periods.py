from datetime import date, timedelta


def get_period_window(next_due_date: date, frequency: str):
    """
    Return (start_date, end_date) for a chore's current period.
    """
    if frequency == "daily":
        delta = timedelta(days=1)
    elif frequency == "weekly":
        delta = timedelta(weeks=1)
    else:
        delta = timedelta(days=1)
    return next_due_date, next_due_date + delta


def get_chore_status(chore, reference_date=None) -> str:
    """
    Determine whether a chore is 'Done', 'Overdue', or 'Pending'.
    """
    if reference_date is None:
        reference_date = date.today()

    # If ChoreCompletion model is available and has completions
    if hasattr(chore, "completions") and chore.completions.all().exists():
        start, end = get_period_window(chore.next_due_date, chore.frequency)
        if chore.completions.filter(completed_at__date__gte=start, completed_at__date__lt=end).exists():
            return "Done"

    if chore.next_due_date < reference_date:
        return "Overdue"
    return "Pending"
