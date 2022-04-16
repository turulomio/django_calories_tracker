
from calories_tracker import serializers
from calories_tracker import models
from calories_tracker.reusing.request_casting import RequestGetString, all_args_are_not_none, RequestGetUrl
from decimal import Decimal
from django.contrib.auth.hashers import check_password
from rest_framework import viewsets, permissions

from rest_framework.decorators import api_view, permission_classes
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
#from rest_framework import viewsets, permissions, status
#from calories_tracker.requests_methods import RequestString


from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import User # new

from django.utils.translation import gettext_lazy as _
# Create your views here.

class MyDjangoJSONEncoder(DjangoJSONEncoder):    
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
#        if isinstance(o, Percentage):
#            return o.value
#        if isinstance(o, Currency):
#            return o.amount
        return super().default(o)
        
        
@api_view(['POST'])
def login(request):
    try:
        user=User.objects.get(username=request.POST.get("username"))
    except User.DoesNotExist:
        return Response("Invalid user")
        
    password=request.POST.get("password")
    pwd_valid=check_password(password, user.password)
    if not pwd_valid:
        return Response("Wrong password")

    if Token.objects.filter(user=user).exists():#Lo borra
        token=Token.objects.get(user=user)
        token.delete()
    token=Token.objects.create(user=user)
    return Response(token.key)
    
@api_view(['POST'])
def logout(request):
    token=Token.objects.get(key=request.POST.get("key"))
    if token is None:
        return Response("Invalid token")
    else:
        token.delete()
        return Response("Logged out")



@csrf_exempt
@api_view(['GET', ])    
def home(request):
    return JsonResponse( True,  encoder=MyDjangoJSONEncoder,     safe=False)
@csrf_exempt
@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated, ])
def Time(request):
    return JsonResponse( timezone.now(), encoder=MyDjangoJSONEncoder,     safe=False)
    
    
class WeightWishesViewSet(viewsets.ModelViewSet):
    queryset = models.WeightWishes.objects.all()
    serializer_class = serializers.WeightWishesSerializer
    permission_classes = [permissions.IsAuthenticated]      
#    
#    def get_queryset(self):
#        active=RequestGetBool(self.request, 'active')
#        account_id=RequestGetInteger(self.request, 'account')
#
#        if account_id is not None and active is not None:
#            return self.queryset.filter(accounts_id=account_id,  active=active)
#        elif active is not None:
#            return self.queryset.filter(active=active)
#        else:
#            return self.queryset.all()

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
        return models.Biometrics.objects.filter(user=self.request.user).order_by("datetime")

class CompaniesViewSet(viewsets.ModelViewSet):
    queryset = models.Companies.objects.all()
    serializer_class = serializers.CompaniesSerializer
    permission_classes = [permissions.IsAuthenticated]


class ElaboratedProductsViewSet(viewsets.ModelViewSet):
    queryset = models.ElaboratedProducts.objects.all()
    serializer_class = serializers.ElaboratedProductsSerializer
    permission_classes = [permissions.IsAuthenticated]      
class FoodTypesViewSet(viewsets.ModelViewSet):
    queryset = models.FoodTypes.objects.all()
    serializer_class = serializers.FoodTypesSerializer
    permission_classes = [permissions.IsAuthenticated]      
class FormatsViewSet(viewsets.ModelViewSet):
    queryset = models.Formats.objects.all()
    serializer_class = serializers.FormatsSerializer
    permission_classes = [permissions.IsAuthenticated]  
    
    
class ProductsFormatsThroughViewSet(viewsets.ModelViewSet):
    queryset = models.ProductsFormatsThrough.objects.all()
    serializer_class = serializers.ProductsFormatsThroughSerializer
    permission_classes = [permissions.IsAuthenticated]  
    ## api/formats/product=url. Search all formats of a product
    def get_queryset(self):
        product=RequestGetUrl(self.request, 'product', models.Products) 
        if all_args_are_not_none(product):
            return models.ProductsFormatsThrough.objects.filter(products=product)
        return self.queryset
    
class MealsViewSet(viewsets.ModelViewSet):
    queryset = models.Meals.objects.all()
    serializer_class = serializers.MealsSerializer
    permission_classes = [permissions.IsAuthenticated]      

class ProductsViewSet(viewsets.ModelViewSet):
    queryset = models.Products.objects.all()
    serializer_class = serializers.ProductsSerializer
    permission_classes = [permissions.IsAuthenticated]      
class ProfilesViewSet(viewsets.ModelViewSet):
    queryset = models.Profiles.objects.all()
    serializer_class = serializers.ProfilesSerializer
    permission_classes = [permissions.IsAuthenticated]      
    
class SystemCompaniesViewSet(viewsets.ModelViewSet):
    queryset = models.SystemCompanies.objects.all()
    serializer_class = serializers.SystemCompaniesSerializer
    permission_classes = [permissions.IsAuthenticated]      

    ## api/system_companies/search=hol. Search all system companies that desn't hava a company jet with hol
    def get_queryset(self):
        search=RequestGetString(self.request, 'search') 
        if all_args_are_not_none(search):
            ## Gets system_companies_id already in companies
            ids_in_companies=models.Companies.objects.filter(user=self.request.user).values("system_companies_id")
            ## Filter by name and exclude already
            return models.SystemCompanies.objects.filter(name__icontains=search).exclude(id__in=[o['system_companies_id'] for o in ids_in_companies])
        return self.queryset


class SystemProductsViewSet(viewsets.ModelViewSet):
    queryset = models.SystemProducts.objects.all()
    serializer_class = serializers.SystemProductsSerializer
    permission_classes = [permissions.IsAuthenticated]      
    
    ## api/system_products/search=hol. Search all system products that desn't hava a product yet with hol
    def get_queryset(self):
        search=RequestGetString(self.request, 'search') 
        if all_args_are_not_none(search):
            ## Gets system_companies_id already in companies
            ids_in_products=models.Products.objects.filter(user=self.request.user).values("system_products_id")
            ## Filter by name and exclude already
            return models.SystemProducts.objects.filter(name__icontains=search).exclude(id__in=[o['system_products_id'] for o in ids_in_products])
        return self.queryset

    
    
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
@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated, ])
def Statistics(request):
    r=[]
    for name, cls in ((_("Activities"), models.Activities), (_("Additive risks"), models.AdditiveRisks), (_("Additives"), models.Additives), (_("Food types"),  models.FoodTypes)):
        r.append({"name": name, "value":cls.objects.all().count()})
    return JsonResponse(r, safe=False)
