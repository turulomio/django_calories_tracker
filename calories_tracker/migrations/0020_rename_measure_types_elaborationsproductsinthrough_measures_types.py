# Generated by Django 4.1.3 on 2022-11-30 06:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('calories_tracker', '0019_elaborationsproductsinthrough_measure_types'),
    ]

    operations = [
        migrations.RenameField(
            model_name='elaborationsproductsinthrough',
            old_name='measure_types',
            new_name='measures_types',
        ),
    ]
