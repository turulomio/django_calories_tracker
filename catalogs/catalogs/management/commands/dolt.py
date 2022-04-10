from django.core.management.base import BaseCommand 
from catalogs.reusing.text_inputs import  input_string
#from catalogs.update_data import update_from_code
from os import system, makedirs, chdir

class Command(BaseCommand):
    help = 'Installs dolt, launches sql console, makes commit, makes push, makes dump in calories_tracker/data/'

    def add_arguments(self, parser):
        pass
                
    def handle(self, *args, **options):
        makedirs("../calories_tracker/data/", exist_ok=True)

        makedirs("dolt", exist_ok=True)
        chdir("dolt")
        system("dolt clone turulomio/dolthub_caloriestracker")
        chdir("..")
            
        chdir("dolt/dolthub_caloriestracker")
        system("dolt pull")
        system("dolt sql-server")
        system("dolt diff")
        commit_messages=input_string("If you want to make a commit, enter a comment. Empty to continue", default="")
        if commit_messages!="":
            system(f"dolt commit -am '{commit_messages}'")
            system("dolt push")            
        system("dolt dump -r json -f --directory=../../../calories_tracker/data")      
#  
#        if input_boolean("Do you want to update new data?", default="T"):
#            chdir("../../..")
#            print(getcwd())
#            update_from_code()
            
        
