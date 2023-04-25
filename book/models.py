from django.db import models


class Book(models.Model):
    class BookCoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        choices=BookCoverChoices.choices, max_length=4, default=BookCoverChoices.HARD
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.IntegerField()

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
