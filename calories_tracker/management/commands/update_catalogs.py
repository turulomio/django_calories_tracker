from django.core.management.base import BaseCommand 
from calories_tracker.update_data import update_from_code

class Command(BaseCommand):
    help = 'Update catalogs from Internet or code'

    def add_arguments(self, parser):
        pass
        

        
    def handle(self, *args, **options):
        update_from_code()
        


