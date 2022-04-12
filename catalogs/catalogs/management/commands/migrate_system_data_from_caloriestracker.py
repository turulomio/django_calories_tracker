from catalogs.reusing.connection_pg import Connection
from django.core.management.base import BaseCommand
from catalogs import models

## Se conecta al dolt mysql_server y a postgres (caloriestracker)
## Solo debe ejecutarse una vez

class Command(BaseCommand):
    help = 'Command to migrate system data from old caloriestracker project (ONLY ONCE AND BY DEVELOPER)'

    def handle(self, *args, **options):
        con_old=Connection()
        con_old.user="postgres"
        con_old.pasword=""
        con_old.server="127.0.0.1"
        con_old.port=5432
        con_old.db="caloriestracker"
        con_old.connect()
        
        models.SystemProductsFormatsThrough.objects.all().delete()
        models.SystemProducts.objects.all().delete()
        models.Formats.objects.all().delete()
        

        for row in con_old.cursor_rows("select * from products order by id"):
            p=models.SystemProducts()
            p.id=row["id"]
            p.name=row["name"]
            p.amount=row["amount"]
            p.fat=row["fat"]
            p.protein=row["protein"]
            p.carbohydrate=row["carbohydrate"]
            if row["companies_id"] is not None:
                p.system_companies=models.SystemCompanies.objects.get(pk=row["companies_id"])
            p.version=row["last"]
            p.calories=row["calories"]
            p.salt=row["salt"]
            p.cholesterol=row["cholesterol"]
            p.sodium=row["sodium"]
            p.potassium=row["potassium"]
            p.fiber=row["fiber"]
            p.sugars=row["sugars"]
            p.saturated_fat=row["saturated_fat"]
            p.food_types=models.FoodTypes.objects.get(pk=row["foodtypes_id"])
            p.obsolete=row["obsolete"]
            p.ferrum=row["obsolete"]
            p.magnesium=row["obsolete"]
            p.phosphor=row["obsolete"]
            p.glutenfree=row["obsolete"]
            p.calcium=row["obsolete"]
            p.save() #Must save before
            arrad=[]
            for ad in row['additives']:
                o=models.Additives.objects.get(id=int(ad))
                arrad.append(o)
            p.additives.add(*arrad)#Enter all objectscts
            p.save() #Must save after
        
        ## Agrego formatos
        for row in con_old.cursor_rows("select distinct(name) from formats order by 1"):
            f=models.Formats()
            f.name=row["name"]
            f.save()
            
        ## Recorro antiguos formatos de system productsts
        for row in con_old.cursor_rows("select * from formats where system_product Is True"):
            fp=models.SystemProductsFormatsThrough()
            fp.amount=row['amount']
            fp.formats=models.Formats.objects.get(name=row['name'])
            fp.system_products=models.SystemProducts.objects.get(id=row['products_id'])
            fp.save()
