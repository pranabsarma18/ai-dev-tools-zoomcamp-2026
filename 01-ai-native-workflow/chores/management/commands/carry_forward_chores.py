from datetime import date, datetime
from django.core.management.base import BaseCommand
from chores.models import Chore
from chores.periods import chore_has_completion_for_period


class Command(BaseCommand):
    help = "Scan for overdue chores and keep them pending without advancing due dates."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date",
            type=str,
            help="Reference date in YYYY-MM-DD format (defaults to today).",
        )

    def handle(self, *args, **options):
        date_str = options.get("date")
        if date_str:
            reference_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            reference_date = date.today()

        overdue_count = 0
        # Scan chores with next_due_date < reference_date
        past_due_chores = Chore.objects.filter(next_due_date__lt=reference_date)

        for chore in past_due_chores:
            if not chore_has_completion_for_period(chore):
                # Chore is overdue and not completed
                # Do NOT advance next_due_date
                overdue_count += 1
                self.stdout.write(
                    f"Chore '{chore.title}' is overdue as of {reference_date}"
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Carry-forward check complete: {overdue_count} overdue chore(s) found."
            )
        )
