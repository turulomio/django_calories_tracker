# Generated by Django 4.1.3 on 2022-11-26 05:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('calories_tracker', '0004_pots'),
    ]

    operations = [
        migrations.CreateModel(
            name='Elaborations',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('diners', models.IntegerField()),
                ('final_amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('robot', models.TextField()),
            ],
            options={
                'db_table': 'elaborations',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Recipes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('last', models.DateTimeField(auto_now_add=True)),
                ('obsolete', models.BooleanField()),
                ('comment', models.TextField()),
                ('food_types', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.foodtypes')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'recipes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RecipesLinksTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'recipes_links_types',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='StirTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'stir_types',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='TemperaturesTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'temperatures_types',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Steps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('stir_types', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.stirtypes')),
                ('temperatures_types', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.temperaturestypes')),
            ],
            options={
                'db_table': 'steps',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='RecipesLinks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField()),
                ('link', models.TextField(null=True)),
                ('content', models.TextField(null=True)),
                ('mime', models.TextField(null=True)),
                ('recipes', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.recipes')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.recipeslinkstypes')),
            ],
            options={
                'db_table': 'recipes_links',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ElaborationsSteps',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('duration', models.TimeField()),
                ('temperature', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('stir', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('comment', models.TextField()),
                ('elaborations', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.elaborations')),
                ('steps', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.steps')),
            ],
            options={
                'db_table': 'elaborations_steps',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ElaborationsProductsInThrough',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('elaborations', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.elaborations')),
                ('products', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.products')),
            ],
        ),
        migrations.AddField(
            model_name='elaborations',
            name='products_in',
            field=models.ManyToManyField(blank=True, through='calories_tracker.ElaborationsProductsInThrough', to='calories_tracker.products'),
        ),
        migrations.AddField(
            model_name='elaborations',
            name='recipes',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.recipes'),
        ),
    ]