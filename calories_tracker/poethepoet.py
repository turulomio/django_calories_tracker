from sys import argv
from calories_tracker.reusing.github import download_from_github
from calories_tracker.reusing.file_functions import replace_in_file

def reusing():
    """
        Actualiza directorio reusing
        poe reusing
        poe reusing --local
    """
    local=False
    if len(argv)==2 and argv[1]=="--local":
        local=True
        print("Update code in local without downloading was selected with --local")
    if local==False:
        download_from_github("turulomio", "reusingcode", "django/request_casting.py", "calories_tracker/reusing")
        download_from_github("turulomio", "reusingcode", "python/connection_pg.py", "calories_tracker/reusing")
        download_from_github("turulomio", "reusingcode", "django/connection_dj.py", "calories_tracker/reusing")
        download_from_github("turulomio", "reusingcode", "python/decorators.py", "calories_tracker/reusing")
        download_from_github("turulomio", "reusingcode", "python/casts.py", "calories_tracker/reusing")
        download_from_github("turulomio", "reusingcode", "python/file_functions.py", "calories_tracker/reusing")
        download_from_github("turulomio", "reusingcode", "python/github.py", "calories_tracker/reusing")
        download_from_github("turulomio", "reusingcode", "python/datetime_functions.py", "calories_tracker/reusing")
        download_from_github("turulomio", "reusingcode", "django/responses_json.py", "calories_tracker/reusing")
        download_from_github("turulomio", "django_moneymoney", "moneymoney/views_login.py", "calories_tracker/reusing")
        download_from_github("turulomio", "django_moneymoney", "moneymoney/factory_helpers.py", "calories_tracker/reusing")

    replace_in_file("calories_tracker/reusing/views_login.py", "moneymoney.reusing", "")
    replace_in_file("calories_tracker/reusing/factory_helpers.py", "from . import serializers", "from .. import serializers")
