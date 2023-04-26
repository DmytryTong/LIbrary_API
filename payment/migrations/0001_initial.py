# Generated by Django 4.2 on 2023-04-24 18:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("borrowing", "0002_borrowing_is_active"),
    ]

    operations = [
        migrations.CreateModel(
            name="Payment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("paid", "Paid")],
                        max_length=50,
                    ),
                ),
                (
                    "type",
                    models.CharField(
                        choices=[("pending", "Pending"), ("paid", "Paid")],
                        max_length=50,
                    ),
                ),
                ("session_url", models.URLField(max_length=255)),
                ("session_id", models.CharField(max_length=255)),
                (
                    "money_to_pay",
                    models.DecimalField(decimal_places=2, max_digits=5),
                ),
                (
                    "borrowing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payments",
                        to="borrowing.borrowing",
                    ),
                ),
            ],
        ),
    ]
