# Generated by Django 4.1.3 on 2022-11-27 12:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calories_tracker', '0011_alter_elaborations_recipes'),
    ]

    operations = [
        migrations.RenameField(
            model_name='elaborations',
            old_name='products_in',
            new_name='elaborations_products_in',
        ),
    ]
