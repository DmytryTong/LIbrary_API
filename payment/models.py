from django.db import models

from borrowing.models import Borrowing


class Payment(models.Model):
    class PaymentStatusEnum(models.TextChoices):
        PENDING = "pending"
        PAID = "paid"

    class PaymentTypeEnum(models.TextChoices):
        PAYMENT = "payment"
        FINE = "fine"

    status = models.CharField(max_length=50, choices=PaymentStatusEnum.choices)
    type = models.CharField(max_length=50, choices=PaymentTypeEnum.choices)
    borrowing = models.ForeignKey(
        to=Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(max_length=255)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self) -> str:
        return f"{self.type} payment for borrowing {self.borrowing.id}"
