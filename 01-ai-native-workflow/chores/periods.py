from datetime import date, timedelta


def get_period_delta(frequency: str) -> timedelta:
    if frequency == "weekly":
        return timedelta(weeks=1)
    return timedelta(days=1)


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
