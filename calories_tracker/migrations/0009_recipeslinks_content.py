# Generated by Django 4.1.3 on 2022-11-27 09:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calories_tracker', '0008_remove_recipeslinks_content_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipeslinks',
            name='content',
            field=models.BinaryField(null=True),
        ),
    ]
