from datetime import datetime
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
    with open("calories_tracker/data/catalogs.json") as f:
        data= process_catalogs(f)
        
    r={}
    r=process_activities(r,data)
    r=process_additive_risks(r,data)
    r=process_weight_wishes(r,data)
    r=process_additives(r,data)
    r=process_food_types(r,data)
    r=process_formats(r,data)
    r=process_system_products(r,data)
    print(f"Update catalogs from code took {datetime.now()-start}")
    
## Used to update a started app
def update_from_github():
    start=datetime.now()
    r={}
    data=process_catalogs()
    r=process_activities(r,data)
    r=process_additive_risks(r,data)
    r=process_weight_wishes(r,data)
    r=process_additives(r,data)
    r=process_food_types(r,data)
    r=process_formats(r,data)
    r=process_system_products(r,data)
    print(f"Update catalogs from code took {datetime.now()-start}")
    
    ## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_catalogs(file_descriptor=None):
    if file_descriptor is None:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/additive_risks.json")
        data =  loads(response.read())
    else:
        data=loads(file_descriptor.read())
    return data
    
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_additive_risks(r, data):
    r["total_additive_risks"]=len(data["additive_risks"])
    r["logs"]=[]
    for d in data["additive_risks"]:
        o=AdditiveRisks()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        try:
            before=AdditiveRisks.objects.get(pk=d["id"])#Crash if not found
            if not o.is_fully_equal(before):
                r["logs"].append({"object":str(o), "log":_("Updated additive risks")})
        except:
            r["logs"].append({"object":str(o), "log":_("Created additive risks")})
        o.save()
    print("AdditiveRisks", "Total:",  r["total_additive_risks"], "Logs:", len(r["logs"]))
    return r        
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_weight_wishes(r,data):
    r["total_weight_wishes"]=len(data["weight_wishes"])
    r["logs"]=[]
    for d in data["weight_wishes"]:
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
    print("WeightWishes", "Total:",  r["total_weight_wishes"], "Logs:", len(r["logs"]))
    return r    
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_activities(r,data):
    r["total_activities"]=len(data["activities"])
    r["logs"]=[]
    for d in data["activities"]:
        o=Activities()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        o.description=checks_and_sets_value(d, "description")
        o.multiplier=checks_and_sets_value(d, "multiplier")
            
        qs_before=Activities.objects.filter(pk=d["id"])#Crash if not found
        if len(qs_before)==0:
            r["logs"].append({"object":str(o), "log":_("Created")})
        else:
            if not o.is_fully_equal(qs_before[0]):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        o.save()
    print("Activities", "Total:",  r["total_activities"], "Logs:", len(r["logs"]))
    return r

## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_additives(r,data):
    r["total_additives"]=len(data["additives"])
    r["logs"]=[]
    for d in data["additives"]:
        o=Additives()
        o.pk=d["id"]
        o.name=checks_and_sets_value(d, "name")
        o.description=checks_and_sets_value(d, "description")
        additive_risks_id=checks_and_sets_value(d,  'additive_risks')
        if additive_risks_id is None:
            o.additive_risks=None
        else:
            o.additive_risks=AdditiveRisks.objects.filter(pk=d["additive_risks"])[0]
        
        qs_before=Additives.objects.filter(pk=d["id"])#Crash if not found
        if len(qs_before)==0:
            r["logs"].append({"object":str(o), "log":_("Created")})
        else:
            if not o.is_fully_equal(qs_before[0]):
                r["logs"].append({"object":str(o), "log":_("Updated")})
        o.save()
    print("Additives", "Total:",  r["total_additives"], "Logs:", len(r["logs"]))
    return r
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_food_types(r,data):
    r["total_food_types"]=len(data["food_types"])
    r["logs"]=[]
    for d in data["food_types"]:
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
    print("FoodTypes", "Total:",  r["total_food_types"], "Logs:", len(r["logs"]))
    return r
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_formats(r,data):
    r["total_formats"]=len(data["formats"])
    r["logs"]=[]
    for d in data["formats"]:
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
    print("Formats", "Total:",  r["total_formats"], "Logs:", len(r["logs"]))
    return r
## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_system_companies(r,data):
    r["total_system_companies"]=len(data["system_companies"])
    r["logs"]=[]
    for d in data["system_companies"]:
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
    print("SystemCompanies", "Total:",  r["total_system_companies"], "Logs:", len(r["logs"]))
    return r

## @param file_descriptor If None uses INternet, if file_descriptor uses file_descriptor read
def process_system_products(r, data):

    r["total_system_products"]=len(data["system_products"])
    r["logs"]=[]
    for dp in data["system_products"]:
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
        system_companies_id=checks_and_sets_value(dp,  'system_companies')
        if system_companies_id is None:
            o.system_companies=None
        else:
            o.system_companies=SystemCompanies.objects.filter(pk=dp["system_companies"])[0]
        o.food_types=FoodTypes.objects.filter(pk=dp["food_types"])[0]
        o.obsolete=bool(dp["obsolete"])
        o.version=string2dtaware(dp['version'], "JsUtcIso", "UTC")
        o.version_description=checks_and_sets_value(dp, "version_description")
        version_parent_id=checks_and_sets_value(dp,  'version_parent')
        if version_parent_id is None:
            o.version_parent=None
        else:
            o.version_parent=SystemProducts.objects.filter(pk=dp["version_parent"])[0]
        
        o.save()
        for da in dp["additives"]:
                o.additives.add(Additives.objects.filter(pk=da['additives'])[0])
                o.save()
               
        qs_before=SystemProducts.objects.filter(pk=dp["id"])#Crash if not found
        if len(qs_before)==0:
            r["logs"].append({"object":str(o), "log":_("Created")})
        else:
            if not o.is_fully_equal(qs_before[0]):
                r["logs"].append({"object":str(o), "log":_("Updated")})

        for df in dp["formats"]:
            qs_sp=SystemProductsFormatsThrough.objects.filter(pk=df["id"])
            if len(qs_sp)==0:
                o=SystemProductsFormatsThrough()
            else:
                o=qs_sp[0]
            o.id=df["id"]
            o.system_products=SystemProducts.objects.get(pk=dp["id"])
            o.formats=Formats.objects.get(pk=df["formats" ])
            o.amount=checks_and_sets_value(df, "amount")
            r["logs"].append({"object":str(o), "log":_("Created")})
            o.save()
    print("SystemProducts", "Total:",  r["total_system_products"], "Logs:", len(r["logs"]))
    
    
    ## Updates all products links
    for user in User.objects.all():
        SystemProducts.update_all_linked_products(user)
    print("Update_all_linked_products")
    return r
