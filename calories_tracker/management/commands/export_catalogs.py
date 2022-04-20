from django.core.management.base import BaseCommand
from calories_tracker.models import Activities, AdditiveRisks, Additives, FoodTypes, Formats, SystemCompanies, SystemProducts, WeightWishes
from tqdm import tqdm

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
        qs_activities=Activities.objects.all().order_by("id")
        qs_additive_risks=AdditiveRisks.objects.all().order_by("id")
        qs_additives=Additives.objects.all().order_by("id")
        qs_food_types=FoodTypes.objects.all().order_by("id")
        qs_formats=Formats.objects.all().order_by("id")
        qs_weight_wishes=WeightWishes.objects.all().order_by("id")
        qs_system_companies=SystemCompanies.objects.all().order_by("id")
        qs_system_products=SystemProducts.objects.all().order_by("id")
        
        s=f"""{{
    "activities": {qs_to_json(qs_activities)}
    "additive_risks": {qs_to_json(qs_additive_risks)}
    "additives": {qs_to_json(qs_additives)}
    "food_types": {qs_to_json(qs_food_types)}
    "formats": {qs_to_json(qs_formats)}
    "weight_wishes": {qs_to_json(qs_weight_wishes)}
    "system_companies": {qs_to_json(qs_system_companies)}
    "system_products": {qs_to_json(qs_system_products)}
}}
"""
        with open("calories_tracker/data/catalogs.json", "w") as f:
            f.write(s)
        

