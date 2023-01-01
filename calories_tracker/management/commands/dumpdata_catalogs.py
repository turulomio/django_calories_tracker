from django.core.management.base import BaseCommand

from django.core.management import call_command


class Command(BaseCommand):
    help = 'Dumpdata command for catalog models only'
        #Generate fixtures
                
    def handle(self, *args, **options):
        call_command(
            "dumpdata", 
            "calories_tracker.activities", 
            "calories_tracker.additives", 
            "calories_tracker.additiverisks", 
            "calories_tracker.foodtypes", 
            "calories_tracker.formats", 
            "calories_tracker.measurestypes", 
            "calories_tracker.recipescategories", 
            "calories_tracker.recipeslinkstypes", 
            "calories_tracker.steps", 
            "calories_tracker.stirtypes", 
            "calories_tracker.systemcompanies", 
            "calories_tracker.systemproducts", 
            "calories_tracker.temperaturestypes", 
            "calories_tracker.weightwishes", 
            "--indent",  "4", 
            "-o", "calories_tracker/fixtures/all.json"
        )
