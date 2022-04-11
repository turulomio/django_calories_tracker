# Generated by Django 4.0.3 on 2022-04-11 10:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activities',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('multiplier', models.DecimalField(decimal_places=4, max_digits=10)),
            ],
            options={
                'db_table': 'activities',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AdditiveRisks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'additive_risks',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Additives',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('additive_risks', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.additiverisks')),
            ],
            options={
                'db_table': 'additives',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Companies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('last', models.DateTimeField(auto_now_add=True)),
                ('obsolete', models.BooleanField()),
            ],
            options={
                'db_table': 'companies',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ElaboratedProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('final_amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('last', models.DateTimeField(auto_now_add=True)),
                ('obsolete', models.BooleanField()),
            ],
            options={
                'db_table': 'elaborated_products',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='FoodTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'food_types',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Formats',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('amount', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
            ],
            options={
                'db_table': 'formats',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('fat', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('protein', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('carbohydrate', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('calories', models.DecimalField(decimal_places=3, max_digits=10)),
                ('salt', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('cholesterol', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('sodium', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('potassium', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('fiber', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('sugars', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('saturated_fat', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('ferrum', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('magnesium', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('phosphor', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('glutenfree', models.BooleanField()),
                ('calcium', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('obsolete', models.BooleanField()),
                ('version', models.DateTimeField(auto_now_add=True)),
                ('version_description', models.TextField(blank=True, null=True)),
                ('additives', models.ManyToManyField(blank=True, to='calories_tracker.additives')),
                ('companies', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.companies')),
                ('elaborated_products', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.elaboratedproducts')),
                ('food_types', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.foodtypes')),
                ('formats', models.ManyToManyField(blank=True, to='calories_tracker.formats')),
            ],
            options={
                'db_table': 'products',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, null=True)),
                ('starts', models.DateTimeField(blank=True, null=True)),
                ('ends', models.DateTimeField(blank=True, null=True)),
                ('male', models.BooleanField(blank=True, null=True)),
                ('birthday', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'profiles',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SystemCompanies',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('last', models.DateTimeField()),
                ('obsolete', models.BooleanField()),
            ],
            options={
                'db_table': 'system_companies',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='WeightWishes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
            ],
            options={
                'db_table': 'weight_wishes',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='SystemProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField()),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('fat', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('protein', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('carbohydrate', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('calories', models.DecimalField(decimal_places=3, max_digits=10)),
                ('salt', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('cholesterol', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('sodium', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('potassium', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('fiber', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('sugars', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('saturated_fat', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('ferrum', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('magnesium', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('phosphor', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('glutenfree', models.BooleanField()),
                ('calcium', models.DecimalField(blank=True, decimal_places=3, max_digits=10, null=True)),
                ('obsolete', models.BooleanField()),
                ('version', models.DateTimeField()),
                ('version_description', models.TextField(blank=True, null=True)),
                ('additives', models.ManyToManyField(blank=True, to='calories_tracker.additives')),
                ('food_types', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.foodtypes')),
                ('formats', models.ManyToManyField(blank=True, to='calories_tracker.formats')),
                ('system_companies', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.systemcompanies')),
                ('version_parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.systemproducts')),
            ],
            options={
                'db_table': 'system_products',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='ProductsInElaboratedProducts',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('elaborated_products', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.elaboratedproducts')),
                ('products', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.products')),
            ],
            options={
                'db_table': 'products_in_elaborated_products',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='products',
            name='system_products',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.systemproducts'),
        ),
        migrations.AddField(
            model_name='products',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='products',
            name='version_parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.products'),
        ),
        migrations.CreateModel(
            name='Meals',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('products', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.products')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'meals',
                'managed': True,
            },
        ),
        migrations.AddField(
            model_name='elaboratedproducts',
            name='food_types',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.foodtypes'),
        ),
        migrations.AddField(
            model_name='elaboratedproducts',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='companies',
            name='system_companies',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.systemcompanies'),
        ),
        migrations.CreateModel(
            name='Biometrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('height', models.DecimalField(decimal_places=2, max_digits=10)),
                ('activities', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.activities')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('weight_wishes', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='calories_tracker.weightwishes')),
            ],
            options={
                'db_table': 'biometrics',
                'managed': True,
            },
        ),
    ]
