# Generated by Django 5.1.4 on 2025-02-03 07:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("bookapp", "0002_book_publisher"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="language",
            field=models.CharField(max_length=100, null=True),
        ),
    ]
