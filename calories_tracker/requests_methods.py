from calories_tracker.models import Products
from calories_tracker.reusing.casts import str2bool, string2list_of_integers
from calories_tracker.reusing.datetime_functions import string2dtaware, string2date
from decimal import Decimal
from urllib import parse
    
def RequestBool(request, field, default=None):
    try:
        r = str2bool(str(request.data.get(field)))
    except:
        r=default
    return r        
def RequestGetBool(request, field, default=None):
    try:
        r = str2bool(request.GET.get(field))
    except:
        r=default
    return r

def RequestGetInteger(request, field, default=None):
    try:
        r = int(request.GET.get(field))
    except:
        r=default
    return r
def RequestInteger(request, field, default=None):
    try:
        r = int(request.data.get(field))
    except:
        r=default
    return r
    
def RequestGetString(request, field, default=None):
    try:
        r = request.GET.get(field, default)
    except:
        r=default
    return r

def RequestGetListOfIntegers(request, field, default=None, separator=","):    
    try:
        r = string2list_of_integers(request.GET.get(field), separator)
    except:
        r=default
    return r
    
    
## Used to get array in this situation calls when investments is an array of integers
    ## To use this methos use axios 
    ##            var headers={...this.myheaders(),params:{investments:this.strategy.investments,otra:"OTTRA"}}
    ##            return axios.get(`${this.$store.state.apiroot}/api/dividends/`, headers)
    ## request.GET returns <QueryDict: {'investments[]': ['428', '447'], 'otra': ['OTRA']}>

def RequestGetArrayOfIntegers(request, field, default=[]):    
    try:
        r=[]
        items=request.GET.getlist(field, [])
        for i in items:
            r.append(int(i))
    except:
        r=default
    return r

def RequestListOfIntegers(request, field, default=None,  separator=","):
    try:
        r = string2list_of_integers(str(request.data.get(field))[1:-1], separator)
    except:
        r=default
    return r

def RequestGetDtaware(request, field, default=None):
    try:
        r = string2dtaware(request.GET.get(field), "JsUtcIso", request.local_zone)
    except:
        r=default
    return r

def RequestDtaware(request, field, default=None):
    try:
        r = string2dtaware(request.data.get(field), "JsUtcIso", request.local_zone)
    except:
        r=default
    return r

def RequestDecimal(request, field, default=None):
    try:
        r = Decimal(request.data.get(field))
    except:
        r=default
    return r
def RequestString(request, field, default=None):
    try:
        r = str(request.data.get(field))
    except:
        r=default
    return r


def obj_from_url(request, url):
    ## FALLA EN APACHE
#    path = urllib.parse.urlparse(url).path
#    print(path)
#    resolved_func, unused_args, resolved_kwargs = resolve(path)
#    print("RESOLVED", resolved_func, unused_args, resolved_kwargs)
#    class_=resolved_func.cls()
#    print("CLASS", class_)
#    class_.request=request
#    return class_.get_queryset().get(pk=int(resolved_kwargs['pk']))

    parts = parse.urlparse(url).path.split("/")
    type=parts[len(parts)-3]
    id=parts[len(parts)-2]
    if type =="products":
        class_=Products
    else:
        print("obj_from_url not found", url)
    return class_.objects.get(pk=id)
    
def id_from_url(request, url):
    ## FALLA EN APACHE
#    path = urllib.parse.urlparse(url).path
#    resolved_func, unused_args, resolved_kwargs = resolve(path)
#    class_=resolved_func.cls()
#    class_.request=request
#    return int(resolved_kwargs['pk'])
    path = parse.urlparse(url).path
    parts=path.split("/")
    return int(parts[len(parts)-2])

## Returns a model obect
def RequestGetUrl(request, field,  default=None):
    try:
        r = obj_from_url(request, request.GET.get(field))
    except:
        r=default
    return r
 
## Returns a model obect
def RequestUrl(request, field,  default=None):
    try:
        r = obj_from_url(request, request.data.get(field))
    except:
        r=default
    return r 
## Returns a model obect
def RequestListUrl(request, field,  default=None):
    try:
        r=[]
        for f in request.data.get(field):
            r.append(obj_from_url(request, f))
    except:
        r=default
    return r

def RequestDate(request, field, default=None):
    try:
        r = string2date(request.data.get(field))
    except:
        r=default
    return r
