# Generated by Django 4.1.3 on 2022-12-08 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calories_tracker', '0028_recipes_datetime'),
    ]

    operations = [
        migrations.AddField(
            model_name='elaborationsproductsinthrough',
            name='ni',
            field=models.BooleanField(default=True),
        ),
    ]
