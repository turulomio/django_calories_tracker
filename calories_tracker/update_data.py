## Update
from json import loads
from urllib import request as urllib_request
from calories_tracker.models import AdditiveRisks, Activities, WeightWishes
_=str


def checks_and_sets_value(d, key):
    if key not in d:
        return None
    if d[key]=="":
        return None
    return d[key]

## Used in first intallation
def update_from_code():
    with open("calories_tracker/data/activities.json") as f:
        process_activities(f)
    with open("calories_tracker/data/additiverisks.json") as f:
        process_additive_risks(f)
    with open("calories_tracker/data/weight_wishes.json") as f:
        process_weight_wishes(f)
    
## Used to update a started app
def update_from_github():
    process_activities()
    process_additive_risks()
    process_weight_wishes()
    
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_additive_risks(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/additiverisks.json")
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
    print(r)
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
    print(r)
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
        o.multiplier=checks_and_sets_value(d, "multiplier")
        try:
            before=Activities.objects.get(pk=d["id"])#Crash if not found
            if not o.is_fully_equal(before):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        except:
            r["logs"].append({"object":str(o), "log":_("Created")})
        o.save()
    print(r)
    return r
