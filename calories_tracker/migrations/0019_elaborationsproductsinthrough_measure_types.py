# Generated by Django 4.1.3 on 2022-11-30 05:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('calories_tracker', '0018_measurestypes_products_density_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='elaborationsproductsinthrough',
            name='measure_types',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.measurestypes'),
            preserve_default=False,
        ),
    ]