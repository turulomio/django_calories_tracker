from django.core.management.base import BaseCommand
from calories_tracker import models
from tqdm import tqdm

from django.core.management import call_command
## qs models must hava json method to convert object to string
def qs_to_json(qs, root_tab=1, end_coma=True):
    r="[\n"
    for o in tqdm(qs):
        r=r+" "*4*(root_tab+1)+o.json() +",\n"
        
    r=r[:-2]+"\n"+" "*4+ "],"
    if end_coma is True:
        return r
    else:
        return r[:-1]

class Command(BaseCommand):
    help = 'Export catalogs to json to allow internet update in Github'

    def handle(self, *args, **options):
        qs_activities=models.Activities.objects.all().order_by("id")
        qs_additive_risks=models.AdditiveRisks.objects.all().order_by("id")
        qs_additives=models.Additives.objects.all().order_by("id")
        qs_food_types=models.FoodTypes.objects.all().order_by("id")
        qs_formats=models.Formats.objects.all().order_by("id")
        qs_weight_wishes=models.WeightWishes.objects.all().order_by("id")
        qs_system_companies=models.SystemCompanies.objects.all().order_by("id")
        qs_system_products=models.SystemProducts.objects.all().order_by("id")
        qs_stir_types=models.StirTypes.objects.all().order_by("id")
        qs_temperatures_types=models.TemperaturesTypes.objects.all().order_by("id")
        qs_recipes_links_types=models.RecipesLinksTypes.objects.all().order_by("id")
        qs_measures_types=models.MeasuresTypes.objects.all().order_by("id")
        qs_steps=models.Steps.objects.all().order_by("id")
        qs_recipes_categories=models.RecipesCategories.objects.all().order_by("id")
        
        s=f"""{{
    "activities": {qs_to_json(qs_activities)}
    "additive_risks": {qs_to_json(qs_additive_risks)}
    "additives": {qs_to_json(qs_additives)}
    "food_types": {qs_to_json(qs_food_types)}
    "formats": {qs_to_json(qs_formats)}
    "weight_wishes": {qs_to_json(qs_weight_wishes)}
    "system_companies": {qs_to_json(qs_system_companies)}
    "system_products": {qs_to_json(qs_system_products)}
    "stir_types": {qs_to_json(qs_stir_types)}
    "temperatures_types": {qs_to_json(qs_temperatures_types)}
    "recipes_links_types": {qs_to_json(qs_recipes_links_types)}
    "measures_types": {qs_to_json(qs_measures_types)}
    "steps": {qs_to_json(qs_steps)}
    "recipes_categories": {qs_to_json(qs_recipes_categories, end_coma="False")}
}}
"""
        with open("calories_tracker/data/catalogs.json", "w") as f:
            f.write(s)
        

        #Generate fixtures
                
        call_command(
            "dumpdata", 
            "calories_tracker.additives", 
            "calories_tracker.additiverisks", 
            "calories_tracker.weightwishes", 
            "calories_tracker.activities", 
            "--indent",  "4", 
            "-o", "calories_tracker/fixtures/all.json"
        )
