from django.core.management.base import BaseCommand
from os import system

class Command(BaseCommand):
    help = 'Run manage.py test with coverage support'
        #Generate fixtures
                
    def handle(self, *args, **options):
        system("coverage run --omit=calories_tracker/reusing/*,/usr/lib64/libreoffice/program/uno.py,calories_tracker/migrations/* manage.py test --settings django_calories_tracker.presettings ; coverage report; coverage html")
