from argparse import ArgumentParser
from catalogs.reusing.github import download_from_github
from os import remove

def replace_in_file(filename, s, r):
    data=open(filename,"r").read()
    remove(filename)
    data=data.replace(s,r)
    f=open(filename, "w")
    f.write(data)
    f.close()

parser=ArgumentParser()
parser.add_argument('--local', help='Parses files without download', action="store_true", default=False)
args=parser.parse_args()      

if args.local==False:
    download_from_github("turulomio", "reusingcode", "python/call_by_name.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/connection_pg.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/listdict_functions.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "django/decorators.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/lineal_regression.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/casts.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/percentage.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/currency.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/github.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/datetime_functions.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/text_inputs.py", "catalogs/reusing")
    download_from_github("turulomio", "reusingcode", "python/libmanagers.py", "catalogs/reusing")

replace_in_file("catalogs/reusing/casts.py", "from currency", "from .currency")
replace_in_file("catalogs/reusing/casts.py", "from percentage", "from .percentage")
replace_in_file("catalogs/reusing/listdict_functions.py", "from casts", "from .casts")

