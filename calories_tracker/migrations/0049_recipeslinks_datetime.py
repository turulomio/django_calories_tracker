"""
Migration: Add `datetime` field to `RecipesLinks` model.

This migration performs a 3-step transition to add a non-nullable `datetime`
field to the existing `recipes_links` table without breaking existing data:
1. Adds the `datetime` field as nullable (`null=True`).
2. Populates `datetime` for all existing `RecipesLinks` records using the
   associated recipe's `last` (last update) timestamp.
3. Alters the `datetime` field to be non-nullable (`null=False`).
"""

from django.db import migrations, models
from django.utils import timezone


def update_recipeslinks_datetime(apps, schema_editor):
    """
    Populates the newly added `datetime` field in `RecipesLinks` using the
    `last` timestamp of the related recipe (or fallback values).
    """
    RecipesLinks = apps.get_model('calories_tracker', 'RecipesLinks')
    
    # Iterate over all existing links and populate datetime from their recipe
    for rl in RecipesLinks.objects.select_related('recipes').all():
        if rl.recipes and rl.recipes.last:
            rl.datetime = rl.recipes.last
        elif rl.recipes and rl.recipes.datetime:
            rl.datetime = rl.recipes.datetime
        else:
            rl.datetime = timezone.now()
        rl.save(update_fields=['datetime'])


class Migration(migrations.Migration):

    dependencies = [
        ('calories_tracker', '0048_pillevents_highlight_late'),
    ]

    operations = [
        # Step 1: Add datetime field allowing null values temporarily
        migrations.AddField(
            model_name='recipeslinks',
            name='datetime',
            field=models.DateTimeField(null=True),
        ),
        # Step 2: Data migration - populate datetime from recipe.last
        migrations.RunPython(
            update_recipeslinks_datetime,
            reverse_code=migrations.RunPython.noop,
        ),
        # Step 3: Enforce non-nullable constraint on datetime field
        migrations.AlterField(
            model_name='recipeslinks',
            name='datetime',
            field=models.DateTimeField(),
        ),
    ]

