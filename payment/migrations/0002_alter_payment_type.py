# Generated by Django 4.2 on 2023-04-25 09:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="type",
            field=models.CharField(
                choices=[("payment", "Payment"), ("fine", "Fine")], max_length=50
            ),
        ),
    ]
