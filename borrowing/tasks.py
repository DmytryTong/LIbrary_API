from django.utils import timezone
from django_q.tasks import async_task

from borrowing.models import Borrowing


def notify_overdue_borrowers():
    now = timezone.now()

    # get all borrowings that are overdue
    overdue_borrowings = Borrowing.objects.filter(expected_return_date__lt=now)

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            user_name = borrowing.user
            title = borrowing.book.title
            expected_return_date = borrowing.expected_return_date
            notification_message = (
                f"Dear {user_name}, you have overdue book {title} that"
                f" should be returned by {expected_return_date}"
            )
            # TODO: send notification to user telegram bot
    else:
        # TODO: send notification telegram bot (No overdue borrowings found)
        pass


# Schedule the task to run every day at a specific time (e.g., 9:00 AM)
async_task("borrowing.tasks.notify_overdue_borrowers", schedule=timezone.now().replace(hour=9, minute=0, second=0))
