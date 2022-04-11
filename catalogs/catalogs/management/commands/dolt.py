from django.core.management.base import BaseCommand 
from catalogs.reusing.text_inputs import  input_string
#from catalogs.update_data import update_from_code
from os import system, makedirs, chdir, remove

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
        
        remove("../../../calories_tracker/data/auth_permission.json")
        remove("../../../calories_tracker/data/django_admin_log.json")
        remove("../../../calories_tracker/data/django_migrations.json")
        remove("../../../calories_tracker/data/django_content_type.json")
        remove("../../../calories_tracker/data/django_session.json")
        remove("../../../calories_tracker/data/auth_user.json")
        remove("../../../calories_tracker/data/auth_user_groups.json")
        remove("../../../calories_tracker/data/auth_user_user_permissions.json")
        remove("../../../calories_tracker/data/auth_group.json")
        remove("../../../calories_tracker/data/auth_group_permissions.json")


 
#  
#        if input_boolean("Do you want to update new data?", default="T"):
#            chdir("../../..")
#            print(getcwd())
#            update_from_code()
            
        
