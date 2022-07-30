from django.conf import settings
from django.core.management.base import BaseCommand
from os import system, chdir
from calories_tracker.__init__ import __version__

class Command(BaseCommand):
    help = 'Create doxygen documentation'  
  
    def add_arguments(self, parser):
        parser.add_argument('--server', type=str, help='Define ssh server', default="127.0.0.1")
        parser.add_argument('--port', type=int, help='Define server',  default=22)
        parser.add_argument('--user', type=str, help='Define ssh server user',  default='root')
        parser.add_argument('--directory', type=str, help='Define ssh server main doxygen directory',  default='/var/www/html/doxygen/')

    def handle(self, *args, **kwargs):
        system("""sed -i -e "41d" doc/Doxyfile""")#Delete line 41
        system("""sed -i -e "41iPROJECT_NUMBER         = {}" doc/Doxyfile""".format(__version__))#Insert line 41
        chdir("doc")
        system("doxygen Doxyfile")
        db=settings.DATABASES['default']

        chdir("html")
        system("/usr/bin/postgresql_autodoc -d {} -h {} -u {} -p {} --password={} -t html".format(db['NAME'], db['HOST'], db['USER'], db['PORT'], db['PASSWORD']))
        system("/usr/bin/postgresql_autodoc -d {} -h {} -u {} -p {} --password={} -t dot_shortfk".format(db['NAME'], db['HOST'], db['USER'], db['PORT'], db['PASSWORD']))
        system("dot -Tpng {0}.dot_shortfk -o {0}_er.png".format(db['NAME']))
        chdir("..")

        command=f"""rsync -avzP -e 'ssh -l {kwargs["user"]} -p {kwargs["port"]} ' html/ {kwargs["server"]}:{kwargs["directory"]}/django_calories_tracker/ --delete-after"""
        print(command)
        system(command)

