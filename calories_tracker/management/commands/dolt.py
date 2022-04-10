from django.core.management.base import BaseCommand 
from calories_tracker.reusing.text_inputs import input_boolean, input_string
from calories_tracker.update_data import update_from_code
from os import system, makedirs, chdir, remove, path, getcwd

class Command(BaseCommand):
    help = 'Installs dolt, launches sql console, makes commit, makes push, makes dump in calories_tracker/data/'

    def add_arguments(self, parser):
        pass
        

        
    def handle(self, *args, **options):
        makedirs("calories_tracker/data/", exist_ok=True)
        # from whichcraft import which
        if path.exists("dolt") is True:            
            if input_boolean("Dolt seems to be installed. Do you want to reinstall it ?", default="F"):
                self.reinstall_dolt()
        else:
            self.reinstall_dolt()
            
        chdir("dolt/dolthub_caloriestracker")
        system("../dolt-linux-amd64/bin/dolt pull")
        system("../dolt-linux-amd64/bin/dolt sql")
        system("../dolt-linux-amd64/bin/dolt diff")
        commit_messages=input_string("If you want to make a commit, enter a comment. Empty to continue", default="")
        if commit_messages!="":
            system(f"../dolt-linux-amd64/bin/dolt commit -am '{commit_messages}'")
            system("../dolt-linux-amd64/bin/dolt push")            
        system("../dolt-linux-amd64/bin/dolt dump -r json -f --directory=../../calories_tracker/data")      
  
        if input_boolean("Do you want to update new data?", default="T"):
            chdir("../..")
            print(getcwd())
            update_from_code()
            
        
        chdir("../..")

