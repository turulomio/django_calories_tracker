# Generated by Django 5.0.8 on 2024-08-24 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calories_tracker", "0045_alter_elaboratedproducts_comment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="systemproducts",
            name="system_companies",
        ),
        migrations.RemoveField(
            model_name="companies",
            name="system_companies",
        ),
        migrations.RemoveField(
            model_name="systemproducts",
            name="additives",
        ),
        migrations.RemoveField(
            model_name="systemproducts",
            name="food_types",
        ),
        migrations.RemoveField(
            model_name="systemproducts",
            name="formats",
        ),
        migrations.RemoveField(
            model_name="systemproducts",
            name="version_parent",
        ),
        migrations.RemoveField(
            model_name="systemproductsformatsthrough",
            name="system_products",
        ),
        migrations.RemoveField(
            model_name="products",
            name="system_products",
        ),
        migrations.RemoveField(
            model_name="systemproductsformatsthrough",
            name="formats",
        ),
        migrations.AddField(
            model_name="products",
            name="openfoodfacts_id",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.DeleteModel(
            name="SystemCompanies",
        ),
        migrations.DeleteModel(
            name="SystemProducts",
        ),
        migrations.DeleteModel(
            name="SystemProductsFormatsThrough",
        ),
    ]
