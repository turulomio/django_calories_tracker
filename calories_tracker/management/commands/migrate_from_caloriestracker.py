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
        con_old=Connection()
        con_old.user="postgres"
        con_old.pasword=""
        con_old.server="127.0.0.1"
        con_old.port=5432
        con_old.db="caloriestracker"
        con_old.connect()
        
        models.Biometrics.objects.all().delete()
        models.ElaboratedProductsProductsInThrough.objects.all().delete()
        models.ElaboratedProducts.objects.all().delete()
        
        user=User.objects.get(pk=1)
        print(user)
        
        for user_old in con_old.cursor_rows("select * from users order by id"):
            user, created = User.objects.get_or_create(
                first_name=user_old["name"],
                username=user_old["name"].lower(),
            )
            
            user.set_password(user.username)
            user.save()
        
            for row in tqdm(con_old.cursor_rows("select * from biometrics where users_id=%s order by id", (user_old["id"], )), desc="Biometrics"):
                p=models.Biometrics()
                p.weight=row['weight']
                p.height=row['height']
                p.datetime=row['datetime']
                p.activities=models.Activities.objects.get(pk=row['activity'])
                p.weight_wishes=models.WeightWishes.objects.get(pk=row['weightwish'])
                p.user=user
                p.save()

            
            if user_old["id"]==1:
                for row in tqdm(con_old.cursor_rows("select * from elaboratedproducts order by id"), desc="ElaboratedProducts"):
                    row_in=con_old.cursor_rows("select * from products_in_elaboratedproducts where elaboratedproducts_id=%s", (row['id'], ))
                    if self.are_all_system_products(row_in):
                        ep=models.ElaboratedProducts()
                        ep.id=row["id"]
                        ep.name=row["name"]
                        ep.final_amount=row["final_amount"]
                        ep.last=row["last"]
                        ep.food_types=models.FoodTypes.objects.get(pk=row['foodtypes_id'])
                        ep.obsolete=row["obsolete"]
                        ep.user=user
                        ep.save()
#                        print("EP", ep.name)
                        
                        for in_ in row_in:
                            pin=models.ElaboratedProductsProductsInThrough()
                            sp=models.SystemProducts.objects.get(pk=in_["products_id"])
                            pin.products=sp.create_and_link_product(user)
                            
#                            print("P", in_, pin.products.name)
                            pin.amount=in_["amount"]
                            pin.elaborated_products=ep
                            pin.save()
                            
                        ep.update_associated_product()



# APRIORI NO LOS MIGRO POR MAL ELABORATED PRODUCT; PERSONAL PRODUCTS
#        for row in tqdm(con_old.cursor_rows("select * from meals order by id"), desc="Meals"):
#            if self.are_all_system_products(row_in):
#                ep=models.Meals()
#                ep.id=row["id"]
#                ep.name=row["name"]
#                ep.final_amount=row["final_amount"]
#                ep.last=row["last"]
#                ep.food_types=models.FoodTypes.objects.get(pk=row['foodtypes_id'])
#                ep.obsolete=row["obsolete"]
#                ep.user=user
#                ep.save()
#                print("EP", ep.name)
#                
#                for in_ in row_in:
#                    pin=models.ElaboratedProductsProductsInThrough()
#                    sp=models.SystemProducts.objects.get(pk=in_["products_id"])
#                    pin.products=sp.create_and_link_product(user)
#                    
#                    print("P", in_, pin.products.name)
#                    pin.amount=in_["amount"]
#                    pin.elaborated_products=ep
#                    pin.save()                    
                
