# Generated by Django 4.1.3 on 2022-12-04 06:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calories_tracker', '0020_rename_measure_types_elaborationsproductsinthrough_measures_types'),
    ]

    operations = [
        migrations.AddField(
            model_name='elaboratedproducts',
            name='recipes',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.recipes'),
        ),
    ]
