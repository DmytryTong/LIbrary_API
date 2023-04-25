from django.utils import timezone

from borrowing import helpers
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
            helpers.send_telegram_notification(message=notification_message)
    else:
        helpers.send_telegram_notification(message="No overdue books today!")
