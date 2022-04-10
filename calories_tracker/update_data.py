## Update
from json import loads
from urllib import request as urllib_request
from calories_tracker.models import AdditiveRisks
_=str


def checks_and_sets_value(d, key):
    if key not in d:
        return None
    if d[key]=="":
        return None
    return d[key]

## Used in first intallation
def update_from_code():
    with open("calories_tracker/data/additiverisks.json") as f:
        process_additive_risks(f)
    
## Used to update a started app
def update_from_github():
    process_additive_risks()
    
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
