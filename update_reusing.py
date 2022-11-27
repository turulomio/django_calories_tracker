from argparse import ArgumentParser
from calories_tracker.reusing.github import download_from_github
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
    download_from_github("turulomio", "reusingcode", "django/request_casting.py", "calories_tracker/reusing")
    download_from_github("turulomio", "reusingcode", "python/call_by_name.py", "calories_tracker/reusing")
    download_from_github("turulomio", "reusingcode", "python/connection_pg.py", "calories_tracker/reusing")
    download_from_github("turulomio", "reusingcode", "django/connection_dj.py", "calories_tracker/reusing")
    download_from_github("turulomio", "reusingcode", "python/listdict_functions.py", "calories_tracker/reusing")
    download_from_github("turulomio", "reusingcode", "python/decorators.py", "calories_tracker/reusing")
    download_from_github("turulomio", "reusingcode", "python/casts.py", "calories_tracker/reusing")
    download_from_github("turulomio", "reusingcode", "python/github.py", "calories_tracker/reusing")
    download_from_github("turulomio", "reusingcode", "python/datetime_functions.py", "calories_tracker/reusing")
    download_from_github("turulomio", "reusingcode", "django/responses_json.py", "calories_tracker/reusing")
    download_from_github("turulomio", "django_moneymoney", "moneymoney/views_login.py", "calories_tracker/reusing")

replace_in_file("calories_tracker/reusing/views_login.py", "moneymoney.reusing", "")
