# Generated by Django 5.2 on 2025-05-04 11:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calories_tracker", "0047_pillevents"),
    ]

    operations = [
        migrations.AddField(
            model_name="pillevents",
            name="highlight_late",
            field=models.BooleanField(
                db_comment="Highlite pill was taken late", default=False
            ),
        ),
    ]
