# Generated by Django 4.2 on 2023-04-24 13:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("borrowing", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="borrowing",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
    ]
