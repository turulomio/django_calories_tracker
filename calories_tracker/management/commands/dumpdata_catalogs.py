from django.core.management.base import BaseCommand

from django.core.management import call_command


## Pruebas con dumpdata y load data
## Creo un registro en systemproducts id=342
## Hago un dumpdata y aparece en el json
## Le edito el nombre de REUSEME a REUSEME2
## Hago loaddata y me devuelve a REUSEME


## Borro el registrto 342
## Ejecuto el loaddata y vuelvo a tenerlo en la base de datos

## Teniendolo en base de datos lo borro del all.json

## Si se hubiera borrado algún modelo o campo desde que fue originalmente creado -i lo ignora

## Conclusión las tablas de fixtures no deben borrar nunca objetos sino ponerlos obsoletos, ya que no lo borra por defecto

## Si se necesitara borrar abría que hacer una load_data comand específico


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
            "calories_tracker.pilleventsstatus", 
            "calories_tracker.recipescategories", 
            "calories_tracker.recipeslinkstypes", 
            "calories_tracker.weightwishes", 
            "--indent",  "4", 
            "-o", "calories_tracker/fixtures/all.json"
        )
