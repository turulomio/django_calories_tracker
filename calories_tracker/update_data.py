## Update
from decimal import Decimal
from json import loads
from urllib import request as urllib_request
from calories_tracker.models import Additives, AdditiveRisks, Activities, WeightWishes, FoodTypes, Formats, SystemCompanies
from calories_tracker.reusing.datetime_functions import string2dtnaive
_=str


def checks_and_sets_value(d, key):
    if key not in d:
        return None
    if d[key]=="":
        return None
    return d[key]

## Used in first intallation
def update_from_code():
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
    
## Used to update a started app
def update_from_github():
    
    process_system_companies()
    process_activities()
    process_additive_risks()
    process_weight_wishes()
    process_additives()
    process_food_types()
    process_formats()
    
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
        o.additive_risks==AdditiveRisks.objects.filter(pk=d["additive_risks_id"])[0]
        
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
        o.amount=Decimal(checks_and_sets_value(d, "amount"))
        
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
        o.last=string2dtnaive(d['last'], "%Y-%m-%d %H:%M:%S.")
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
