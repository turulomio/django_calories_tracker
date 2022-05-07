from calories_tracker import serializers
from calories_tracker import models
from calories_tracker.reusing.listdict_functions import listdict_order_by
from calories_tracker.reusing.request_casting import RequestGetString, RequestGetDate, all_args_are_not_none, RequestUrl, RequestString, RequestDate, RequestBool, RequestListUrl
from calories_tracker.update_data import update_from_data
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Count, Min
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from json import loads
from rest_framework import viewsets, permissions,  status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from statistics import median
from urllib import request as urllib_request

class MyDjangoJSONEncoder(DjangoJSONEncoder):    
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
#        if isinstance(o, Percentage):
#            return o.value
#        if isinstance(o, Currency):
#            return o.amount
        return super().default(o)
        
        

@csrf_exempt
@permission_classes([permissions.IsAuthenticated, ])
def CatalogManager(request):
    return JsonResponse( settings.CATALOG_MANAGER, encoder=MyDjangoJSONEncoder, safe=False)

@csrf_exempt
@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated, ])
def Time(request):
    return JsonResponse( timezone.now(), encoder=MyDjangoJSONEncoder,     safe=False)
    
    
class WeightWishesViewSet(viewsets.ModelViewSet):
    queryset = models.WeightWishes.objects.all()
    serializer_class = serializers.WeightWishesSerializer
    permission_classes = [permissions.IsAuthenticated]      

class ActivitiesViewSet(viewsets.ModelViewSet):
    queryset = models.Activities.objects.all()
    serializer_class = serializers.ActivitiesSerializer
    permission_classes = [permissions.IsAuthenticated]     

class AdditiveRisksViewSet(viewsets.ModelViewSet):
    queryset = models.AdditiveRisks.objects.all()
    serializer_class = serializers.AdditiveRisksSerializer
    permission_classes = [permissions.IsAuthenticated]      

class AdditivesViewSet(viewsets.ModelViewSet):
    queryset = models.Additives.objects.all()
    serializer_class = serializers.AdditivesSerializer
    permission_classes = [permissions.IsAuthenticated]      

class BiometricsViewSet(viewsets.ModelViewSet):
    queryset = models.Biometrics.objects.all().order_by("datetime")
    serializer_class = serializers.BiometricsSerializer
    permission_classes = [permissions.IsAuthenticated]      

    def get_queryset(self):
        day=RequestGetDate(self.request, "day")
        if all_args_are_not_none(day):        
            return models.Biometrics.objects.select_related("user").select_related("user__profiles").select_related("activities").filter(user=self.request.user, datetime__date__lte=day).order_by("-datetime")[:1]
        return models.Biometrics.objects.select_related("user").select_related("user__profiles").select_related("activities").filter(user=self.request.user).order_by("datetime")

class CompaniesViewSet(viewsets.ModelViewSet):
    queryset = models.Companies.objects.select_related("system_companies").all()
    serializer_class = serializers.CompaniesSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).annotate(uses=Count("products", distinct=True)).order_by("name")


class ElaboratedProductsViewSet(viewsets.ModelViewSet):
    queryset = models.ElaboratedProducts.objects.all()    
#    queryset = models.ElaboratedProducts.objects.prefetch_related(
#        Prefetch(
#            'products_in',
#            queryset=models.ElaboratedProductsProductsInThrough.objects.select_related("products", "elaborated_products").all(),
#        ),
#    ).all()
    serializer_class = serializers.ElaboratedProductsSerializer
    permission_classes = [permissions.IsAuthenticated]      
    
    def get_queryset(self):
        #print(dir(self.queryset[0]), self.queryset[0].__class__)
        return self.queryset.filter(user=self.request.user).order_by("name")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        qs_products_in=models.ElaboratedProductsProductsInThrough.objects.filter(elaborated_products=instance)
        qs_products_in.delete()
        #Destroy asoociated product
        qs=models.Products.objects.filter(elaborated_products=instance  )
        if len(qs)>0:
            qs[0].delete()
        self.perform_destroy(instance)
        return JsonResponse( True, encoder=MyDjangoJSONEncoder,     safe=False)
    
    
class FoodTypesViewSet(viewsets.ModelViewSet):
    queryset = models.FoodTypes.objects.all()
    serializer_class = serializers.FoodTypesSerializer
    permission_classes = [permissions.IsAuthenticated]      
class FormatsViewSet(viewsets.ModelViewSet):
    queryset = models.Formats.objects.all()
    serializer_class = serializers.FormatsSerializer
    permission_classes = [permissions.IsAuthenticated]  

    
class MealsViewSet(viewsets.ModelViewSet):
    queryset = models.Meals.objects.all()
    serializer_class = serializers.MealsSerializer
    permission_classes = [permissions.IsAuthenticated]      

    ## api/formats/product=url. Search all formats of a product
    def get_queryset(self):
        day=RequestGetDate(self.request, 'day') 
        if all_args_are_not_none(day):
            return models.Meals.objects.filter(user=self.request.user, datetime__date=day).order_by("datetime")
        return self.queryset

    ## delete_several. meals as an array
    @action(detail=False, methods=['post'])
    def delete_several(self, request):
        meals=RequestListUrl(request, "meals", models.Meals)
        if all_args_are_not_none(meals):
            for meal in meals:
                meal.delete()
            return Response('Meals.delete_several success')
        return Response('Meals.delete_several failure')

class ProductsViewSet(viewsets.ModelViewSet):
    queryset = models.Products.objects.all()
    serializer_class = serializers.ProductsSerializer
    permission_classes = [permissions.IsAuthenticated]      
    def get_queryset(self):
        return models.Products.objects.select_related("companies","system_products", "elaborated_products", ).prefetch_related("additives", "additives__additive_risks").prefetch_related("productsformatsthrough_set").annotate(uses=Count("meals", distinct=True)+Count("elaboratedproductsproductsinthrough", distinct=True)).filter(user=self.request.user).order_by("name")



class ProfilesViewSet(viewsets.ModelViewSet):
    queryset = models.Profiles.objects.all()
    serializer_class = serializers.ProfilesSerializer
    permission_classes = [permissions.IsAuthenticated]      
    
class SystemCompaniesViewSet(viewsets.ModelViewSet):
    queryset = models.SystemCompanies.objects.all().order_by("name")
    serializer_class = serializers.SystemCompaniesSerializer
    permission_classes = [permissions.IsAuthenticated]      

    ## api/system_products/search_not_in=hol. Search all system products that desn't hava a product yet with hol
    ## api/system_companies/search=hol. Search all system companies that desn't hava a company jet with hol
    def get_queryset(self):
        search_not_in=RequestGetString(self.request, 'search_not_in') 
        search=RequestGetString(self.request, 'search') 
        if all_args_are_not_none(search_not_in):
            ## Gets system_companies_id already in companies
            ids_in_companies=models.Companies.objects.filter(user=self.request.user).values("system_companies_id")
            ## Filter by name and exclude already
            return models.SystemCompanies.objects.filter(name__icontains=search).exclude(id__in=[o['system_companies_id'] for o in ids_in_companies])
        if all_args_are_not_none(search):
            return models.SystemCompanies.objects.filter(name__icontains=search).order_by("name")
        return self.queryset


class SystemProductsViewSet(viewsets.ModelViewSet):
    queryset = models.SystemProducts.objects.select_related("system_companies").prefetch_related("additives",  "additives__additive_risks","systemproductsformatsthrough_set").all()
    serializer_class = serializers.SystemProductsSerializer
    permission_classes = [permissions.IsAuthenticated]      
    
    ## api/system_products/search_not_in=hol. Search all system products that desn't hava a product yet with hol
    ## api/system_products/search=hol. Search all system products that contains search string in name
    def get_queryset(self):
        search_not_in=RequestGetString(self.request, 'search_not_in') 
        search=RequestGetString(self.request, 'search') 
        if all_args_are_not_none(search_not_in):
            ## Gets system_companies_id already in companies
            ids_in_products=models.Products.objects.filter(user=self.request.user).values("system_products_id")
            ## Filter by name and exclude already
            return self.queryset.filter(name__icontains=search).exclude(id__in=[o['system_products_id'] for o in ids_in_products]).order_by("name")
        if all_args_are_not_none(search):
            return self.queryset.filter(name__icontains=search).order_by("name")
        return self.queryset
    
@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])

## Links a systemproduct to a product. No todos los system products están por eso se linka
def SystemProduct2Product(request):
    system_products=RequestUrl(request, "system_products", models.SystemProducts)
    if all_args_are_not_none(system_products):
        system_products.update_linked_product(request.user)
        return JsonResponse( True, encoder=MyDjangoJSONEncoder,     safe=False)
    return JsonResponse( False, encoder=MyDjangoJSONEncoder,     safe=False)
    
@csrf_exempt
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])

## Links a systemproduct to a product. No todos los system products están por eso se linka
def SystemCompany2Company(request):
    system_companies=RequestUrl(request, "system_companies", models.SystemCompanies)
    if all_args_are_not_none(system_companies):
        system_companies.update_linked_company(request.user)
        return JsonResponse( True, encoder=MyDjangoJSONEncoder,     safe=False)
    return JsonResponse( False, encoder=MyDjangoJSONEncoder,     safe=False)
    
@csrf_exempt
@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated, ])
@transaction.atomic
def Settings(request):
    p=models.get_profile(request.user)
    if request.method == 'GET':
        r={}
        r['first_name']=request.user.first_name
        r['last_name']=request.user.last_name
        r['last_login']=request.user.last_login     
        r['email']=request.user.email     
        r['birthday']=p.birthday
        r['male']=p.male
        return JsonResponse( r, encoder=MyDjangoJSONEncoder,     safe=False)
    elif request.method == 'POST':
        #Personal settings
        birthday=RequestDate(request,"birthday")
        male=RequestBool(request, "male")
        last_name=RequestString(request, "last_name")
        first_name=RequestString(request, "first_name")
        email=RequestString(request, "email")
        if all_args_are_not_none(birthday, male, first_name, last_name, email):
            p.birthday=birthday
            p.male=male
            p.save()
            request.user.first_name=first_name
            request.user.last_name=last_name
            request.user.email=email
            request.user.save()
            return JsonResponse(True, safe=False)
        return JsonResponse(False, safe=False)

@csrf_exempt
@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated, ])
def Statistics(request):
    r=[]
    for name, cls in ((_("Activities"), models.Activities), (_("Additive risks"), models.AdditiveRisks), (_("Additives"), models.Additives), (_("Food types"),  models.FoodTypes)):
        r.append({"name": name, "value":cls.objects.all().count()})
    return JsonResponse(r, safe=False)


@csrf_exempt
@api_view(['POST', ])
@permission_classes([permissions.IsAuthenticated, ])
@transaction.atomic
def MaintenanceCatalogsUpdate(request):
    start=datetime.now()
    auto=RequestBool(request, "auto", False) ## Uses automatic request with settings globals investing.com   
    if auto is True:
        response = urllib_request. urlopen("https://raw.githubusercontent.com/turulomio/django_calories_tracker/main/calories_tracker/data/catalogs.json")
        data =  loads(response. read())
        update_from_data(data)
    else:
        # if not GET, then proceed
        if "json_file1" not in request.FILES:
            return Response({'status': 'You must upload a file'}, status=status.HTTP_404_NOT_FOUND)
        else:
            json_file = request.FILES["json_file1"]
            
        if not json_file.name.endswith('.json'):
            return Response({'status': 'File has not .json extension'}, status=status.HTTP_404_NOT_FOUND)

        data=loads(json_file.read())
        update_from_data(data)

    print(f"Update catalogs took {datetime.now()-start}")

    return JsonResponse( True, encoder=MyDjangoJSONEncoder, safe=False)
    
    

@csrf_exempt
@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated, ])
def Curiosities(request):
    r=[]
    
    qs_products=models.Products.objects.filter(user=request.user)
    qs_meals=models.Meals.objects.select_related("products").filter(user=request.user)
    dict_meals_by_day_calories={}
    qs_biometrics=models.Biometrics.objects.filter(user=request.user).order_by("datetime")
    for m in qs_meals:
        dict_meals_by_day_calories[str(m.datetime.date())]=dict_meals_by_day_calories.get(str(m.datetime.date()), 0)+m.getProductComponent("calories")
    
    
    if len(qs_meals)>0:
        value=models.Meals.objects.filter(user=request.user).aggregate(Min("datetime"))["datetime__min"]
        print(value)
        r.append({
            "question":_("Since when there is data in the database?"), 
            "answer": _("The first data is from {0}").format(value)
        })
        
        
        
    sel_p=None
    sel_cal=0
    for p in qs_products:
        tmp_cal=p.getProductComponentIn100g("calories")
        if tmp_cal>sel_cal:
            sel_p=p
            sel_cal=tmp_cal
    r.append({
        "question":_("Which is the product with highest calories in 100 g?"), 
        "answer":_("The product with highest calories is '{0}' with {1} calories.").format(sel_p.fullname(), round(sel_cal, 0))
    })


    if len(qs_meals)>0:
        sel_m=None
        sel_cal=0
        for m in qs_meals:
            tmp_cal=m.getProductComponent("calories")
            if tmp_cal>sel_cal:
                sel_m=m
                sel_cal=tmp_cal
        r.append({
            "question":_("Which is the meal with highest calories I had eaten?"), 
            "answer": _("The meal with the highest calories I ate was '{}' with '{}' calories. I ate {}g at {}.").format(sel_m.products.fullname(), round(sel_cal, 0), round(sel_m.amount, 0), sel_m.datetime), 
        })
        
        
        
    if len(qs_meals)>0:
        sel_key=""
        sel_value=0
        for key, value in dict_meals_by_day_calories.items():
            if value>sel_value:
                sel_key=key
                sel_value=value 
        r.append({
            "question":_("When did I take the highest calories amount in a day?"), 
            "answer": _("The day I took the highest amount of calories was '{}' and I took {}.").format(sel_key, round(sel_value, 0)), 
        })


    if len(qs_biometrics)>0:
        sel_b=None
        sel_weight=0
        for b in qs_biometrics:
            if b.weight>sel_weight:
                sel_b=b
                sel_weight=b.weight
        r.append({
            "question":_("When did I have my highest weight?"), 
            "answer": _("My highest weight was {} kg at {}").format(sel_weight, sel_b.datetime), 
        })
        

    if len(qs_biometrics)>0:
        sel_b=None
        sel_weight=10000
        for b in qs_biometrics:
            if b.weight<sel_weight:
                sel_b=b
                sel_weight=b.weight
        r.append({
            "question":_("When did I have my lowest weight?"), 
            "answer": _("My lowest weight was {} kg at {}").format(sel_weight, sel_b.datetime), 
        })
        
        
    if len(qs_biometrics)>0:
        median_=median([b.weight for b in qs_biometrics])
        r.append({
            "question":_("Which is my median weight?"), 
            "answer": _("My median weight is {} kg").format(median_), 
        })
        
    return JsonResponse(r, safe=False)

@csrf_exempt
@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated, ])
def MealsRanking(request):
    from_date=RequestGetDate(request, "from_date")
    qs_meals=models.Meals.objects.select_related("products").filter(user=request.user)
    if from_date is not None:
        qs_meals=qs_meals.filter(datetime__date__gte=from_date)
    dict_meals_by_day_amount={}
    for m in qs_meals:
        dict_meals_by_day_amount[m.products.id]=dict_meals_by_day_amount.get(m.products.id, 0)+m.amount

    r=[]
    for key, value in dict_meals_by_day_amount.items():
        r.append({
            "product": request.build_absolute_uri(reverse('products-detail', args=(key, ))), 
            "amount": value, 
        })

    r=listdict_order_by(r, "amount", reverse=True)
    return JsonResponse(r, safe=False)
