from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from calories_tracker import models
from glob import glob
from os import path
from mimetypes import guess_type
from tqdm import tqdm
class Command(BaseCommand):
    help = 'Imports recipes from directory, recursively'  
  
    def add_arguments(self, parser):
        parser.add_argument('--directory', type=str, help='Directory where recipes are', required=True)
        parser.add_argument('--user_id', type=str, help='User id to import recipes to', required=True)


    def handle(self, *args, **kwargs):
        user=User.objects.get(pk=kwargs["user_id"])
        filenames=[]
        for filename in glob( kwargs["directory"]+"**/*", recursive=True):
            if path.isfile(filename):
                filenames.append(filename)
                
        for filename in tqdm(filenames):
            content=open(filename, "rb").read()
            name_without=path.basename(path.splitext(filename)[0])
            #Ignora si es > 100MB
            if len(content)>100000000:
                continue
            
            ##Ignora si está grabada
            qs=models.Recipes.objects.filter(name=name_without)
            if qs.count()>0:
                continue
            
            r=models.Recipes()
            r.name=name_without
            r.food_types=models.FoodTypes.objects.get(pk=19)
            r.obsolete=False                
            r.user=user
            r.guests=False
            r.soon=False
            r.save()
            
            rl=models.RecipesLinks()
            rl.description="Migrado de directorio de mis recetas"
            rl.type=models.RecipesLinksTypes.objects.get(pk=6)
            rl.recipes=r
            rl.content=content
            rl.mime=guess_type(filename)[0]
            rl.save()


