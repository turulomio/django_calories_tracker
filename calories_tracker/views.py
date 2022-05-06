
from calories_tracker import serializers
from calories_tracker import models
from calories_tracker.reusing.request_casting import RequestGetString, RequestGetDate, all_args_are_not_none, RequestUrl, RequestString, RequestDate, RequestBool, RequestListUrl
from decimal import Decimal
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.models import Count#, Prefetch
from django.http import JsonResponse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

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
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])
## Stores a filename encoded to base64 in a global variable
## Global: base64_{name}.{extension}
## @param only binary data, don't have to include data:image/png;base64 or similar
## Para guardarlo a ficheros se puede hacer
##    f=open(f"/tmp/{filename}", "wb")
##    f.write(b64decode(data))
##    f.close()
### @global_ For Example: base64_assetsreport_report_annual_chart.png
def Binary2Global(request):
    pass
    
    
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
