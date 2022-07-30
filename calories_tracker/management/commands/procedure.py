from django.core.management.base import BaseCommand
from calories_tracker.__init__ import __version__, __versiondatetime__
from os import system

class Command(BaseCommand):
    help = 'New release procedure'

    def handle(self, *args, **options):
        print(f"Updating versions of calories_tracker frontend project to {__version__} and {__versiondatetime__}")
        d=__versiondatetime__
        system (f"""sed -i '3s/.*/  "version": "{__version__}",/' ../calories_tracker/package.json""")
        system (f"""sed -i '11s/.*/        version: "{__version__}",/' ../calories_tracker/src/store.js""")
        system (f"""sed -i '12s/.*/        versiondate: new Date({d.year}, {d.month-1}, {d.day}, {d.hour}, {d.minute}),/' ../calories_tracker/src/store.js""")

        print()
        print(f"""To release a new version:
DJANGO_CALORIES_TRACKER
  * Change version and version datetime in calories_tracker/__init__.py
  * python manage.py procedure
  * python manage.py makedbmessages
  * python manage.py makemessages --all
  * mcedit calories_tracker/locale/es/LC_MESSAGES/django.po
  * python manage.py compilemessages
  * python manage.py doxygen
  * git commit -a -m 'django_calories_tracker-{__version__}'
  * git push
  * Hacer un nuevo tag en GitHub de django_calories_tracker

CALORIES_TRACKER
  * Cambiar a calories_tracker project
  * Add release changelog in README.md
  * npm run i18n:report
  * mcedit src/locales/es.json
  * git commit -a -m 'calories_tracker-{__version__}'
  * git push
  * Hacer un nuevo tag en GitHub de calories_tracker
""")

