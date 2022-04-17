# Los productos elaborados solo se migran si todos sus productos son de systema
# Los meals solo se migran si todos sus productos son de systema
# Si se usa un system products se copia con una funcion

from calories_tracker.reusing.connection_pg import Connection
from django.core.management.base import BaseCommand
from calories_tracker import models
from django.contrib.auth.models import User
from tqdm import tqdm
## Se conecta al dolt mysql_server y a postgres (caloriestracker)
## Solo debe ejecutarse una vez

class Command(BaseCommand):
    help = 'Command to migrate system data from old caloriestracker project (ONLY ONCE AND BY DEVELOPER)'

    def are_all_system_products(self, row_in):
        for in_ in row_in:
            if in_["system_product"]==False:
                return False
        return True

    def handle(self, *args, **options):
        print("This must be done with an empty database with systems catalogs updated")
        print("So you have to ddo python manage.py update_catalogs")
        
        con_old=Connection()
        con_old.user="postgres"
        con_old.pasword=""
        con_old.server="127.0.0.1"
        con_old.port=5432
        con_old.db="caloriestracker"
        con_old.connect()
                
        
        ## MIGRANDO USUARIOS
        for user_old in con_old.cursor_rows("select * from users order by id"):
            user, created = User.objects.get_or_create(
                first_name=user_old["name"],
                username=user_old["name"].lower(),
            )
            
            user.set_password(user.username)
            user.save()
        
            ## MIGRANDO BIOMETRIS
            for row in tqdm(con_old.cursor_rows("select * from biometrics where users_id=%s order by id", (user_old["id"], )), desc="Biometrics"):
                p=models.Biometrics()
                p.weight=row['weight']
                p.height=row['height']
                p.datetime=row['datetime']
                p.activities=models.Activities.objects.get(pk=row['activity'])
                p.weight_wishes=models.WeightWishes.objects.get(pk=row['weightwish'])
                p.user=user
                p.save()

            products_old_to_new={} ## Diccionario para mapear los antiguos personal_products a actuales products ["system_prodducts#id"]
            companies_old_to_new={} ## Diccionario para mapear los antiguos personal_products a actuales products ["system_companies#id"]
            
            ## MIGRANDO PERSONAL COMPANIES
            for row in tqdm(con_old.cursor_rows("select * from personalcompanies order by id"), desc="PersonalCompanies"):
                p=models.Companies()
                p.name=row["name"]
                p.last=row["last"]
                p.obsolete=row["obsolete"]
                p.user=user
                p.save()
                companies_old_to_new[f"False#{row['id']}"]=p.id
                
            
            ## MIGRANDO PRODUCTOS PERSONALES
            for row in tqdm(con_old.cursor_rows("select * from personalproducts where elaboratedproducts_id is null order by id"), desc="PersonalProducts"):
                p=models.Products()
                p.name=row["name"]
                p.amount=row["amount"]
                p.fat=row["fat"]
                p.protein=row["protein"]
                p.carbohydrate=row["carbohydrate"]
                if row["companies_id"] is not None:
                    if row['system_company'] is True:
                        sc=models.SystemCompanies.objects.get(pk=row["companies_id"])
                        p.companies=sc.update_linked_company(user)
                        companies_old_to_new[f"{row['system_company']}#{row['companies_id']}"]=p.companies.id
                    else: #personal companies
                        p.companies=models.Companies.objects.get(pk=companies_old_to_new[f"{row['system_company']}#{row['companies_id']}"])
                p.last=row["last"]
                p.calories=row["calories"]
                p.salt=row["salt"]
                p.cholesterol=row["cholesterol"]
                p.sodium=row["sodium"]
                p.potassium=row["potassium"]
                p.fiber=row["fiber"]
                p.sugars=row["sugars"]
                p.saturated_fat=row["saturated_fat"]
                p.food_types=models.FoodTypes.objects.get(pk=row["foodtypes_id"])
                p.ferrum=row["ferrum"]
                p.magnesium=row["magnesium"]
                p.phosphor=row["phosphor"]
                p.calcium=row["calcium"]
                p.glutenfree=row["glutenfree"]
                p.obsolete=row["obsolete"]
                p.user=user
                p.save()
                
                p.additives.set(row["additives"])
                p.save()
                products_old_to_new[f"False#{row['id']}"]=p.id
                
            
            ## MIGRANDO PRODUCTOS ELABORADOS
            for row in tqdm(con_old.cursor_rows("select * from elaboratedproducts order by id"), desc="ElaboratedProducts"):
                row_in=con_old.cursor_rows("select * from products_in_elaboratedproducts where elaboratedproducts_id=%s", (row['id'], ))
                ep=models.ElaboratedProducts()
                ep.id=row["id"]
                ep.name=row["name"]
                ep.final_amount=row["final_amount"]
                ep.last=row["last"]
                ep.food_types=models.FoodTypes.objects.get(pk=row['foodtypes_id'])
                ep.obsolete=row["obsolete"]
                ep.user=user
                ep.save()
                
                for in_ in row_in:
                    pin=models.ElaboratedProductsProductsInThrough()
                    try:
                        if in_["system_product"] is True:
                            sp=models.SystemProducts.objects.get(pk=in_["products_id"])
                            pin.products=sp.update_linked_product(user)
                            products_old_to_new[f"{in_['system_product']}#{in_['products_id']}"]=pin.products.id
                        else: #Personal product
                            pin.products=models.Products.objects.get(pk=products_old_to_new[f"{in_['system_product']}#{in_['products_id']}"])
                    except:
                        print("Product", f"{in_['system_product']}#{in_['products_id']}", "was not found" )
                        continue
                    pin.amount=in_["amount"]
                    pin.elaborated_products=ep
                    pin.save()
                        
                ## Asocia el nuevo al viejos
                asoc=ep.update_associated_product()
                asoc_old=con_old.cursor_one_row("Select * from personalproducts where elaboratedproducts_id=%s", (row['id'], ))
                products_old_to_new[f"False#{asoc_old['id']}"]=asoc.id
                    
            ## MIGRANDO MEALS
            for row in tqdm(con_old.cursor_rows("select * from meals where users_id=%s order by id", (user_old["id"], )), desc="Meals"):
                m=models.Meals()
                m.user=user
                m.amount=row["amount"]
                try:
                    if row["system_product"] is True:
                        sp=models.SystemProducts.objects.get(pk=row["products_id"])
                        m.products=sp.update_linked_product(user)
                        products_old_to_new[f"{row['system_product']}#{row['products_id']}"]=pin.products.id
                    else: #Personal product
                        m.products=models.Products.objects.get(pk=products_old_to_new[f"{row['system_product']}#{row['products_id']}"])
                except:
                    print("Product", f"{row['system_product']}#{row['products_id']}", "was not found" )
                    continue
                m.datetime=row["datetime"]
                m.save()
                
