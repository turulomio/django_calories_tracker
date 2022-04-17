from datetime import datetime
from decimal import Decimal
from json import loads
from urllib import request as urllib_request
from calories_tracker.models import Additives, AdditiveRisks, SystemProductsFormatsThrough,  Activities, WeightWishes, FoodTypes, Formats, SystemCompanies, SystemProducts
from calories_tracker.reusing.datetime_functions import string2dtaware
_=str

from django.contrib.auth.models import User

def checks_and_sets_value(d, key):
    if key not in d:
        return None
    if d[key]=="":
        return None
    return d[key]

## Used in first intallation
def update_from_code():
    start=datetime.now()
    with open("calories_tracker/data/system_companies.json") as f:
        process_system_companies(f)
    with open("calories_tracker/data/activities.json") as f:
        process_activities(f)
    with open("calories_tracker/data/additive_risks.json") as f:
        process_additive_risks(f)
    with open("calories_tracker/data/weight_wishes.json") as f:
        process_weight_wishes(f)
    with open("calories_tracker/data/additives.json") as f:
        process_additives(f)
    with open("calories_tracker/data/food_types.json") as f:
        process_food_types(f)
    with open("calories_tracker/data/formats.json") as f:
        process_formats(f)
    with open("calories_tracker/data/system_products.json") as p,  open("calories_tracker/data/system_products_additives.json") as a:
        process_system_products(p, a)
    with open("calories_tracker/data/catalogs_systemproductsformatsthrough.json") as f:
        process_catalogs_systemproductsformatsthrough(f)
    print(f"Update catalogs from code took {datetime.now()-start}")
    
## Used to update a started app
def update_from_github():
    
    process_system_companies()
    process_activities()
    process_additive_risks()
    process_weight_wishes()
    process_additives()
    process_food_types()
    process_formats()
    process_system_products()
    process_catalogs_systemproductsformatsthrough()
    
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_additive_risks(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/additive_risks.json")
        data =  loads(response.read())
    else:
        data=loads(file_descriptor.read())

    r={}
    r["total"]=len(data["rows"])
    r["logs"]=[]
    for d in data["rows"]:
        o=AdditiveRisks()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        try:
            before=AdditiveRisks.objects.get(pk=d["id"])#Crash if not found
            if not o.is_fully_equal(before):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        except:
            r["logs"].append({"object":str(o), "log":_("Created")})
        o.save()
    print("AdditiveRisks", "Total:",  r["total"], "Logs:", len(r["logs"]))
    return r        
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_weight_wishes(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/weight_wishes.json")
        data =  loads(response.read())
    else:
        data=loads(file_descriptor.read())

    r={}
    r["total"]=len(data["rows"])
    r["logs"]=[]
    for d in data["rows"]:
        o=WeightWishes()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        try:
            before=WeightWishes.objects.get(pk=d["id"])#Crash if not found
            if not o.is_fully_equal(before):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        except:
            r["logs"].append({"object":str(o), "log":_("Created")})
        o.save()
    print("WeightWishes", "Total:",  r["total"], "Logs:", len(r["logs"]))
    return r    
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_activities(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/activities.json")
        data =  loads(response.read())
    else:
        data=loads(file_descriptor.read())

    r={}
    r["total"]=len(data["rows"])
    r["logs"]=[]
    for d in data["rows"]:
        o=Activities()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        o.description=checks_and_sets_value(d, "description")
        o.multiplier=Decimal(checks_and_sets_value(d, "multiplier"))
            
        qs_before=Activities.objects.filter(pk=d["id"])#Crash if not found
        if len(qs_before)==0:
            r["logs"].append({"object":str(o), "log":_("Created")})
        else:
            if not o.is_fully_equal(qs_before[0]):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        o.save()
    print("Activities", "Total:",  r["total"], "Logs:", len(r["logs"]))
    return r

## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_additives(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/additives.json")
        data =  loads(response.read())
    else:
        data=loads(file_descriptor.read())

    r={}
    r["total"]=len(data["rows"])
    r["logs"]=[]
    for d in data["rows"]:
        o=Additives()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        o.description=checks_and_sets_value(d, "description")
        additive_risks_id=checks_and_sets_value(d,  'additive_risks_id')
        if additive_risks_id is None:
            o.additive_risks=None
        else:
            o.additive_risks=AdditiveRisks.objects.filter(pk=d["additive_risks_id"])[0]
        
        qs_before=Additives.objects.filter(pk=d["id"])#Crash if not found
        if len(qs_before)==0:
            r["logs"].append({"object":str(o), "log":_("Created")})
        else:
            if not o.is_fully_equal(qs_before[0]):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        o.save()
    print("Additives", "Total:",  r["total"], "Logs:", len(r["logs"]))
    return r
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_food_types(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/food_types.json")
        data =  loads(response.read())
    else:
        data=loads(file_descriptor.read())

    r={}
    r["total"]=len(data["rows"])
    r["logs"]=[]
    for d in data["rows"]:
        o=FoodTypes()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        
        qs_before=FoodTypes.objects.filter(pk=d["id"])#Crash if not found
        if len(qs_before)==0:
            r["logs"].append({"object":str(o), "log":_("Created")})
        else:
            if not o.is_fully_equal(qs_before[0]):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        o.save()
    print("FoodTypes", "Total:",  r["total"], "Logs:", len(r["logs"]))
    return r
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_formats(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/formats.json")
        data =  loads(response.read())
    else:
        data=loads(file_descriptor.read())

    r={}
    r["total"]=len(data["rows"])
    r["logs"]=[]
    for d in data["rows"]:
        o=Formats()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        
        qs_before=Formats.objects.filter(pk=d["id"])#Crash if not found
        if len(qs_before)==0:
            r["logs"].append({"object":str(o), "log":_("Created")})
        else:
            if not o.is_fully_equal(qs_before[0]):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        o.save()
    print("Formats", "Total:",  r["total"], "Logs:", len(r["logs"]))
    return r
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_system_companies(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/system_companies.json")
        data =  loads(response.read())
    else:
        data=loads(file_descriptor.read())

    r={}
    r["total"]=len(data["rows"])
    r["logs"]=[]
    for d in data["rows"]:
        o=SystemCompanies()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        o.last=string2dtaware(d['last'], "%Y-%m-%d %H:%M:%S.", "UTC")
        o.obsolete=bool(int(d["obsolete"]))
        
        qs_before=SystemCompanies.objects.filter(pk=d["id"])#Crash if not found
        if len(qs_before)==0:
            r["logs"].append({"object":str(o), "log":_("Created")})
        else:
            if not o.is_fully_equal(qs_before[0]):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        o.save()
    print("SystemCompanies", "Total:",  r["total"], "Logs:", len(r["logs"]))
    return r

## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_system_products(file_descriptor_p=None, file_descriptor_a=None):
    if file_descriptor_p is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/system_products.json")
        products =  loads(response.read())
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/system_products_additives.json")
        additives =  loads(response.read())
    else:
        products=loads(file_descriptor_p.read())
        additives=loads(file_descriptor_a.read())

    rp={}
    rp["total"]=len(products["rows"])
    rp["logs"]=[]
    for dp in products["rows"]:
        o=SystemProducts()
        o.id=dp['id']
        o.name = dp['name']
        o.amount=checks_and_sets_value(dp, "amount")
        o.fat=checks_and_sets_value(dp, "fat")
        o.protein=checks_and_sets_value(dp, "protein")
        o.carbohydrate=checks_and_sets_value(dp, "carbohydrate")
        o.calories=checks_and_sets_value(dp, "calories")
        o.salt=checks_and_sets_value(dp, "salt")
        o.cholesterol=checks_and_sets_value(dp, "cholesterol")
        o.sodium=checks_and_sets_value(dp, "sodium")
        o.potassium=checks_and_sets_value(dp, "potassium")
        o.fiber=checks_and_sets_value(dp, "fiber")
        o.sugars=checks_and_sets_value(dp, "sugars")
        o.saturated_fat=checks_and_sets_value(dp, "saturated_fat")
        o.ferrum=checks_and_sets_value(dp, "ferrum")
        o.magnesium=checks_and_sets_value(dp, "magnesium")
        o.phosphor=checks_and_sets_value(dp, "phosphor")
        o.calcium=checks_and_sets_value(dp, "calcium")
        o.glutenfree=bool(dp['glutenfree'])
        system_companies_id=checks_and_sets_value(dp,  'system_companies_id')
        if system_companies_id is None:
            o.system_companies=None
        else:
            o.system_companies=SystemCompanies.objects.filter(pk=dp["system_companies_id"])[0]
        o.food_types=FoodTypes.objects.filter(pk=dp["food_types_id"])[0]
        o.obsolete=bool(dp["obsolete"])
        o.version=string2dtaware(dp['version'], "%Y-%m-%d %H:%M:%S.", "UTC")
        o.version_description=checks_and_sets_value(dp, "version_description")
        version_parent_id=checks_and_sets_value(dp,  'version_parent_id')
        if version_parent_id is None:
            o.version_parent=None
        else:
            o.version_parent=SystemProducts.objects.filter(pk=dp["version_parent_id"])[0]
        
        o.save()
        for da in additives["rows"]:
            if da["systemproducts_id"]==dp['id']:
                o.additives.add(Additives.objects.filter(pk=da['additives_id'])[0])
               
        qs_before=SystemProducts.objects.filter(pk=dp["id"])#Crash if not found
        if len(qs_before)==0:
            rp["logs"].append({"object":str(o), "log":_("Created")})
        else:
            if not o.is_fully_equal(qs_before[0]):
                rp["logs"].append({"object":str(o), "log":_("Updated")})
        o.save()
        
    
    print("SystemProducts", "Total:",  rp["total"], "Logs:", len(rp["logs"]))
    return rp

## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_catalogs_systemproductsformatsthrough(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/catalogs_systemproductsformatsthrough.json")
        data =  loads(response.read())
    else:
        data=loads(file_descriptor.read())
        
    SystemProductsFormatsThrough.objects.all().delete()#Borra todos ya que se pueden borra en edición en dolthub y no se usan mas que para calculo no hay referencias.

    r={}
    r["total"]=len(data["rows"])
    r["logs"]=[]
    for d in data["rows"]:
        o=SystemProductsFormatsThrough()
        o.id=d["id"]
        o.system_products=SystemProducts.objects.get(pk=d["system_products_id"])
        o.formats=Formats.objects.get(pk=d["formats_id" ])
        o.amount=checks_and_sets_value(d, "amount")
        r["logs"].append({"object":str(o), "log":_("Created")})
        o.save()
    print("SystemProductsFormatsThrough", "Total:",  r["total"], "Logs:", len(r["logs"]))
    
    
    ## Updates all products links
    for user in User.objects.all():
        SystemProducts.update_all_linked_products(user)
    print("Update_all_linked_products")
    return r
