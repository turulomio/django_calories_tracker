from calories_tracker.reusing.connection_dj import cursor_rows
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Command to dump database translatable string to hardcoded_strings.py'

    def handle(self, *args, **options):
        strings=[]
        for row in cursor_rows("select name from weight_wishes order by name"):
            strings.append("_('{}')".format(row["name"]))
        for row in cursor_rows("select name from activities order by name"):
            strings.append("_('{}')".format(row["name"]))
        for row in cursor_rows("select name from additive_risks order by name"):
            strings.append("_('{}')".format(row["name"]))
        for row in cursor_rows("select name from food_types order by name"):
            strings.append("_('{}')".format(row["name"]))
        for row in cursor_rows("select name from formats order by name"):
            strings.append("_('{}')".format(row["name"]))
        for row in cursor_rows("select name from recipes_links_types order by name"):
            strings.append("_('{}')".format(row["name"]))
        for row in cursor_rows("select name from recipes_categories order by name"):
            strings.append("_('{}')".format(row["name"]))
        for row in cursor_rows("select name from measures_types order by name"):
            strings.append("_('{}')".format(row["name"]))
            
        strings.sort()
        f=open("calories_tracker/hardcoded_strings.py", "w")
        f.write("from django.utils.translation import gettext_lazy as _\n")
        for s in strings:
            f.write(f"{s}\n")
        f.close()

