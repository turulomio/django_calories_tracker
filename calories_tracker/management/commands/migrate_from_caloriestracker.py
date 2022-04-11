from moneymoney.reusing.connection_dj import cursor_rows
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Command to generate products from old caloriestracker project'

    def handle(self, *args, **options):
        for row in cursor_rows("select * from products order by id"):
            s=f"insert into system_products(id, name) values ({row['id'],  row['name']})"
            print(s)
            
            
#        
#        strings.sort()
#        f=open("moneymoney/hardcoded_strings.py", "w")
#        f.write("from django.utils.translation import gettext_lazy as _\n")
#        for s in strings:
#            f.write(f"{s}\n")
#        f.close()

