# Generated by Django 4.0.3 on 2022-04-12 06:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogs', '0006_remove_formats_amount_alter_formats_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='systemproducts',
            name='formats',
        ),
    ]