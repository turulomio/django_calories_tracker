# Generated by Django 4.0.3 on 2022-04-11 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0002_remove_formats_last'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemproducts',
            name='formats',
            field=models.ManyToManyField(to='catalogs.formats'),
        ),
        migrations.AlterField(
            model_name='formats',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]