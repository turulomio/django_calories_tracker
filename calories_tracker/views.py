from calories_tracker import serializers
from calories_tracker import models
from calories_tracker.reusing.connection_dj import show_queries, show_queries_function
from calories_tracker.reusing.decorators import ptimeit
from calories_tracker.reusing.datetime_functions import dtaware2string
from calories_tracker.reusing.listdict_functions import listdict_order_by
from calories_tracker.reusing.request_casting import RequestGetString, RequestGetUrl, RequestGetDate, all_args_are_not_none, RequestUrl, RequestString, RequestDate, RequestBool, RequestListUrl, id_from_url, object_from_url, RequestInteger
from calories_tracker.reusing.responses_json import MyDjangoJSONEncoder, json_success_response, json_data_response
from calories_tracker.update_data import update_from_data
from datetime import datetime
from decimal import Decimal
from django.db import transaction
from django.db.models import Count, Min, Prefetch
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from itertools import product
from json import loads
from rest_framework import viewsets, permissions,  status, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from statistics import median
from urllib import request as urllib_request

ptimeit
show_queries
show_queries_function

class GroupCatalogManager(permissions.BasePermission):
    """Permiso que comprueba si pertenece al grupo Interventor """
    def has_permission(self, request, view):
        return request.user.groups.filter(name="CatalogManager").exists()
    


@permission_classes([permissions.IsAuthenticated, ])
@api_view(['GET', ])
def CatalogManager(request):
    return JsonResponse( request.user.groups.filter(name="CatalogManager").exists(), encoder=MyDjangoJSONEncoder, safe=False)


@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated, ])
def Time(request):
    return JsonResponse( timezone.now(), encoder=MyDjangoJSONEncoder, safe=False)
    
    
class WeightWishesViewSet(viewsets.ModelViewSet):
    queryset = models.WeightWishes.objects.all()
    serializer_class = serializers.WeightWishesSerializer
    permission_classes = [permissions.IsAuthenticated]      
    http_method_names=['get']

class ActivitiesViewSet(viewsets.ModelViewSet):
    queryset = models.Activities.objects.all()
    serializer_class = serializers.ActivitiesSerializer
    permission_classes = [permissions.IsAuthenticated]     
    http_method_names=['get']

class AdditiveRisksViewSet(viewsets.ModelViewSet):
    queryset = models.AdditiveRisks.objects.all()
    serializer_class = serializers.AdditiveRisksSerializer
    permission_classes = [permissions.IsAuthenticated]      
    http_method_names=['get']

class AdditivesViewSet(viewsets.ModelViewSet):
    queryset = models.Additives.objects.all()
    serializer_class = serializers.AdditivesSerializer
    permission_classes = [permissions.IsAuthenticated]      
    http_method_names=['get']

class BiometricsViewSet(viewsets.ModelViewSet):    
    """
        <div style="background-color:BurlyWood;">
        
        <h3>BiometricsViewSet custom documentation</h3>
        
        <ul>
            <li><strong>GET /api/biometrics/?day=2022-01-01</strong> Gets biometrics of request user at day 2022-01-01</li>
            <li><strong>GET /api/biometrics/</strong> Gets all biometrics of request user</li>
        </ul>
        </div>
    """

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
    serializer_class = serializers.ElaboratedProductsSerializer
    permission_classes = [permissions.IsAuthenticated]      
    
    def get_queryset(self):
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
    
    

class ElaborationsViewSet(viewsets.ModelViewSet):
    queryset = models.Elaborations.objects.all().select_related("recipes")
    serializer_class = serializers.ElaborationsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        recipes=RequestGetUrl(self.request, "recipes", models.Recipes)
        if all_args_are_not_none(recipes):
            return self.queryset.filter(recipes=recipes, recipes__user=self.request.user)
        return self.queryset.filter(recipes__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        models.ElaborationsProductsInThrough.objects.filter(elaborations=instance).delete()
        models.ElaborationsSteps.objects.filter(elaborations=instance).delete()
        instance.recipes.last=timezone.now()
        instance.recipes.save()
        self.perform_destroy(instance)
        return Response(status.HTTP_204_NO_CONTENT)
        
        
    @action(detail=True, methods=['POST'], name='Hace un update masivo de todos los steps', url_path="update_steps", url_name='update_steps', permission_classes=[permissions.IsAuthenticated])
    def update_steps(self, request, pk=None):
        elaboration=self.get_object()
        ##Lista con todos que se va quitando para borrar al final
        to_delete=list(models.ElaborationsSteps.objects.filter(elaborations=elaboration).values_list("id", flat=True))
                
        for d in request.data["steps"]:
            es=models.ElaborationsSteps()
            if "url" in d:
                if  d["url"] is not None:
                    id=id_from_url(d["url"])
                    to_delete.remove(id)# Va borrando de la lista a borrar los que están en el post
                    es=models.ElaborationsSteps.objects.get(pk=id)
                
            es.elaborations=object_from_url(d["elaborations"], models.Elaborations)
            es.order=d["order"]
            es.steps=object_from_url(d["steps"], models.Steps)
            es.duration=d["duration"]
            es.temperatures_types=None if d["temperatures_types"] is None else object_from_url(d["temperatures_types"], models.TemperaturesTypes)
            es.temperatures_values=d["temperatures_values"]
            es.stir_types=None if d["stir_types"] is None else object_from_url(d["stir_types"], models.StirTypes)
            es.stir_values=d["stir_values"]
            es.container=None if d["container"] is None else object_from_url(d["container"], models.ElaborationsContainers)
            es.container_to=None if d["container_to"] is None else object_from_url(d["container_to"], models.ElaborationsContainers)
            es.comment=d["comment"]
            es.save()
            
            products_in_step=[]
            for pis in d["products_in_step"]:
                item=object_from_url(pis, models.ElaborationsProductsInThrough)
                products_in_step.append(item)
            es.products_in_step.set(products_in_step)#Añade en bloque
            es.save()
            
        models.ElaborationsSteps.objects.filter(id__in=to_delete).delete()       
        r=[]
        for es in models.ElaborationsSteps.objects.filter(elaborations=elaboration).order_by("order"):
            r.append(serializers.ElaborationsStepsSerializer(es, context={'request': request}).data)
        return json_data_response(True, r,  "Steps actualizados")

    @action(detail=True, methods=['POST'], name='It creates and elaborated product from a recipe elaboration', url_path="create_elaborated_product", url_name='create_elaborated_product', permission_classes=[permissions.IsAuthenticated])
    def create_elaborated_product(self, request, pk=None):
        elaboration = self.get_object()
        #Sets all elaborated products and products from this recipe obsolete
        for ep in models.ElaboratedProducts.objects.filter(recipes=elaboration.recipes):
            ep.obsolete=True
            ep.save()
            models.Products.objects.filter(elaborated_products=ep).update(obsolete=True)
        #Creates a new elaborated product
        ep=models.ElaboratedProducts()
        ep.last=timezone.now()
        ep.name=_("{0} for {1} diners ({2})").format(elaboration.recipes.name, elaboration.diners, dtaware2string(ep.last, "%Y-%m-%d %H:%M:%S"))
        ep.final_amount=elaboration.final_amount
        ep.food_types=elaboration.recipes.food_types
        ep.obsolete=False
        ep.user=request.user
        ep.recipes=elaboration.recipes
        ep.save()
        #Creates asociated product
        ep.update_associated_product()
        #Adds all products_in
        for rpi in elaboration.elaborationsproductsinthrough_set.all():
            epi=models.ElaboratedProductsProductsInThrough()
            epi.amount=rpi.final_grams()
            epi.products=rpi.products
            epi.elaborated_products=ep
            epi.save()
        #Returns created elaborated product serialized
        return JsonResponse(serializers.ElaboratedProductsSerializer(ep, context={'request': request}).data, status=200)

    @action(detail=True, methods=['POST'], name='It creates a PDF for this elaboration', url_path="generate_pdf", url_name='generate_pdf', permission_classes=[permissions.IsAuthenticated])
    def generate_pdf(self, request, pk=None):
        from calories_tracker.unogenerator_files import response_report_elaboration
        elaboration = self.get_object()
        return response_report_elaboration(request, elaboration)
        
    @action(detail=True, methods=['POST'], name='Create a new automatic elaboration', url_path="create_automatic_elaboration", url_name='create_automatic_elaboration', permission_classes=[permissions.IsAuthenticated])
    def create_automatic_elaboration(self, request, pk=None):
        def new_amount(old_pi,  diners):
            if diners<= old_pi.elaborations.diners:#Disminuyo la receta divido nada más, ignorando automatic_percentage
                return Decimal(diners)*old_pi.amount/Decimal(old_pi.elaborations.diners)
            else:#Aumeto la ActivitiesViewSet
                diff_diners=diners-old_pi.elaborations.diners
                one_diner=old_pi.amount/Decimal(old_pi.elaborations.diners)
                return old_pi.amount+one_diner*diff_diners*old_pi.automatic_percentage/100
                
            ################################
        old=self.get_object()
        diners=RequestInteger(request, "diners", None)
        
        if all_args_are_not_none(diners):
            
            new=models.Elaborations()
            new.diners=diners
            new.recipes=old.recipes
            new.final_amount=Decimal(diners)*old.final_amount/Decimal(old.diners)
            new.automatic=True
            new.save()
            
            dict_old_new={}#Hay que mapear los antiguos con los nuevos para luego añadirlos a los steps
            #ingredients
            for old_pi in old.elaborationsproductsinthrough_set.all():
                new_pi=models.ElaborationsProductsInThrough()
                new_pi.products=old_pi.products
                new_pi.elaborations=new
                new_pi.measures_types=old_pi.measures_types
                new_pi.amount=new_amount(old_pi, diners)
                new_pi.comment=old_pi.comment
                new_pi.ni=old_pi.ni
                new_pi.automatic_percentage=old_pi.automatic_percentage
                new_pi.save()
                dict_old_new[old_pi]=new_pi
            new.save()
            
            for old_container in old.elaborations_containers.all():
                new_container=models.ElaborationsContainers()
                new_container.name=old_container.name
                new_container.elaborations=new
                new_container.save()
        
            for old_step in old.elaborations_steps.all():
                new_step=models.ElaborationsSteps()
                new_step.order=old_step.order
                new_step.elaborations=new
                new_step.steps=old_step.steps
                new_step.duration=old_step.duration
                new_step.comment=old_step.comment
                new_step.container=old_step.container
                new_step.container_to=old_step.container_to
                new_step.temperatures_types=old_step.temperatures_types
                new_step.temperatures_values=old_step.temperatures_values
                new_step.stir_types=old_step.stir_types
                new_step.stir_values=old_step.stir_values
                new_step.save()
                productsin=[]
                for pis in old_step.products_in_step.all():
                    productsin.append(dict_old_new[pis])
                new_step.products_in_step.set(productsin)
                new_step.save()
                
            return json_data_response(True, [],  "Steps updated")
        return json_data_response(False, [],  "Diners error")
        
        
class ElaborationsContainersViewSet(viewsets.ModelViewSet):
    queryset = models.ElaborationsContainers.objects.all()
    serializer_class = serializers.ElaborationsContainersSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        elaboration=RequestGetUrl(self.request, "elaboration", models.Elaborations)
        if all_args_are_not_none(elaboration):        
            return self.queryset.filter(elaborations=elaboration, elaborations__recipes__user=self.request.user)
        return self.queryset.filter(elaborations__recipes__user=self.request.user)

class ElaborationsExperiencesViewSet(viewsets.ModelViewSet):
    queryset = models.ElaborationsExperiences.objects.all()
    serializer_class = serializers.ElaborationsExperiencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        elaboration=RequestGetUrl(self.request, "elaboration", models.Elaborations)
        if all_args_are_not_none(elaboration):        
            return self.queryset.filter(elaborations=elaboration, elaborations__recipes__user=self.request.user)
        return self.queryset.filter(elaborations__recipes__user=self.request.user)

class ElaborationsStepsViewSet(viewsets.ModelViewSet):
    queryset = models.ElaborationsSteps.objects.all().order_by("order")
    serializer_class = serializers.ElaborationsStepsSerializer
    permission_classes = [permissions.IsAuthenticated]
        
    def get_queryset(self):
        elaboration=RequestGetUrl(self.request, "elaboration", models.Elaborations)
        if all_args_are_not_none(elaboration):        
            return self.queryset.filter(elaborations=elaboration, elaborations__recipes__user=self.request.user).order_by("order")
        return self.queryset.filter(elaborations__recipes__user=self.request.user).order_by("order")

class ElaborationsProductsInThrough(viewsets.ModelViewSet):
    queryset = models.ElaborationsProductsInThrough.objects.all()
    serializer_class = serializers.ElaborationsProductsInThroughSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        elaboration=RequestGetUrl(self.request, "elaboration", models.Elaborations)
        if all_args_are_not_none(elaboration):        
            return self.queryset.filter(elaborations=elaboration)
        return self.queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.elaborations.recipes.last=timezone.now()
        instance.elaborations.recipes.save()
        return viewsets.ModelViewSet.destroy(self, request, args, kwargs)

class StepsViewSet(viewsets.ModelViewSet):
    queryset = models.Steps.objects.all()
    serializer_class = serializers.StepsSerializer
    permission_classes = [permissions.IsAuthenticated]
        
    @action(detail=True, methods=["get"],url_path='wordings', url_name='wordings')
    def wordings(self, request, pk=None):
        step=self.get_object()
##   id  | duration | comment | elaborations_id | steps_id | order | container_id | container_to_id | stir_types_id | stir_values | temperatures_types_id | temperatures_values 
##-----+----------+---------+-----------------+----------+-------+--------------+-----------------+---------------+-------------+-----------------------+---------------------
## 848 | 00:09:00 |         |              20 |        1 |     2 |            9 |                 |             1 |           1 |                     1 |                 120

        r={}
        # Variaciones con repetiión para poder ver todos los resultados posibles
        for can_products_in_step,  can_container,  can_container_to, can_temperatures, can_stir,  has_comment in product([True, False], repeat=6):
            if (    (step.can_products_in_step==False and can_products_in_step==True) or
                    (step.can_container==False and can_container==True) or
                    (step.can_container_to==False and can_container_to==True) or
                    (step.can_temperatures==False and can_temperatures==True) or
                    (step.can_stir==False and can_stir==True) or 
                    #Mandatory
                    (step.man_products_in_step==True and can_products_in_step==False) or
                    (step.man_container==True and can_container==False) or
                    (step.man_container_to==True and can_container_to==False) or
                    (step.man_temperatures==True and can_temperatures==False) or
                    (step.man_stir==True and can_stir==False)
                            
                ):
                        pass
            else:
                        es=models.ElaborationsSteps.objects.get(pk=838)
                        es.steps=step
                        es.container_to=es.container
                        es.temperatures_types=models.TemperaturesTypes.objects.get(pk=2)
                        es.temperatures_values=-2
                                                        
                        if has_comment:
                            es.comment="Esto es un comentario"
                        if can_stir is False:
                            es.stir_types=None
                        if can_temperatures is False:
                            es.temperatures_types=None
                        r[str((can_products_in_step, can_container, can_container_to, can_temperatures, can_stir, has_comment))]={#Dictionary for get unique elements
                            "can_products_in_step":can_products_in_step, 
                            "can_container":can_container, 
                            "can_container_to":can_container_to, 
                            "can_temperatures":can_temperatures, 
                            "can_stir":can_stir, 
                            "has_comment": has_comment, 
                            "wording": es.wording(), 
                        }
        list_=[]
        for k, v in r.items():
            list_.append(v)
        return json_data_response(True, list_,  "Steps actualizados")

class FoodTypesViewSet(viewsets.ModelViewSet):
    queryset = models.FoodTypes.objects.all()
    serializer_class = serializers.FoodTypesSerializer
    permission_classes = [permissions.IsAuthenticated]      
    http_method_names=['get']

class FormatsViewSet(viewsets.ModelViewSet):
    queryset = models.Formats.objects.all()
    serializer_class = serializers.FormatsSerializer
    permission_classes = [permissions.IsAuthenticated]  
    http_method_names=['get']
    
class MeasuresTypesViewSet(viewsets.ModelViewSet):
    queryset = models.MeasuresTypes.objects.all()
    serializer_class = serializers.MeasuresTypesSerializer
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
    @extend_schema(
        parameters=[
            OpenApiParameter(name='meals', description='Meal to delete (List)', required=True, type=OpenApiTypes.URI), 
        ],
    )
    @action(detail=False, methods=['post'])
    def delete_several(self, request):
        meals=RequestListUrl(request, "meals", models.Meals)
        if all_args_are_not_none(meals):
            for meal in meals:
                meal.delete()
            return Response('Meals.delete_several success')
        return Response('Meals.delete_several failure')
        
@extend_schema_view(
    list=extend_schema(
        description="The list action returns all available actions."
    ),
    create=extend_schema(
        description="The create action expects the fields `name`, creates a new object and returns it."
    ),
    retrieve=extend_schema(
        description="The retrieve action returns a single object selected by `id`."
    )
)
class PotsViewSet(viewsets.ModelViewSet):
    queryset = models.Pots.objects.all()
    serializer_class = serializers.PotsSerializer
    permission_classes = [permissions.IsAuthenticated]      
    
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        if instance.photo is not None:
            instance.photo.delete()
        return Response(status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'GET'])
@permission_classes([permissions.IsAuthenticated, ])
@transaction.atomic
def ProductsDataTransfer(request):
    if request.method=="GET":
        product_from=RequestGetUrl(request, "product_from", models.Products)
        product_to=RequestGetUrl(request, "product_to", models.Products)
    
        if all_args_are_not_none(product_from, product_to):
            r=[]
            for p in (product_from, product_to):
                r.append({
                    "product": request.build_absolute_uri(reverse('products-detail', args=(p.id, ))), 
                    "products_in": models.ElaboratedProductsProductsInThrough.objects.filter(products=p).count(), 
                    "meals": models.Meals.objects.filter(products=p).count(),
                })
            return JsonResponse( r, encoder=MyDjangoJSONEncoder, safe=False)
    else:# request.method=="POST":
        product_from=RequestUrl(request, "product_from", models.Products)
        product_to=RequestUrl(request, "product_to", models.Products)
    
        if all_args_are_not_none(product_from, product_to):
            for pi in models.ElaboratedProductsProductsInThrough.objects.filter(products=product_from):
                pi.products=product_to
                pi.save()
            for m in models.Meals.objects.filter(products=product_from):
                m.products=product_to
                m.save()            
            return JsonResponse( True, encoder=MyDjangoJSONEncoder, safe=False)


class ProductsViewSet(viewsets.ModelViewSet):
    queryset = models.Products.objects.all()
    serializer_class = serializers.ProductsSerializer
    permission_classes = [permissions.IsAuthenticated]      
    def get_queryset(self):
        return models.Products.objects.select_related("companies","system_products", "elaborated_products", ).prefetch_related("additives", "additives__additive_risks").prefetch_related("productsformatsthrough_set").annotate(uses=Count("meals", distinct=True)+Count("elaboratedproductsproductsinthrough", distinct=True)).filter(user=self.request.user).order_by("name")

class FilesViewSet(mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Files.objects.all()
    serializer_class = serializers.FilesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @action(detail=True, methods=["get"],url_path='thumbnail', url_name='thumbnail')
    def thumbnail(self, request, pk=None):
        qs_files=models.Files.objects.filter(user=request.user, pk=pk).only("thumbnail")
        return Response(qs_files[0].get_thumbnail_js())

    @action(detail=True, methods=["get"],url_path='content', url_name='content')
    def content(self, request, pk=None):
        qs_files=models.Files.objects.filter(user=request.user, pk=pk).only("content")
        return Response(qs_files[0].get_content_js())
    
## Only with recipes_Links to get file for main image
class RecipesViewSet(viewsets.ModelViewSet):
    queryset = models.Recipes.objects.all().prefetch_related("recipes_links", "recipes_links__type", "recipes_categories", 
        Prefetch("recipes_links__files",  models.Files.objects.all().only("id", "mime", "size"))
    )
    serializer_class = serializers.RecipesSerializer
    permission_classes = [permissions.IsAuthenticated]      
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='String used to search recipes. ', required=True, type=str), 
        ],
    )
    def get_queryset(self):
        search=RequestGetString(self.request, 'search') 
        if all_args_are_not_none(search):
            
            if search==":SOON":
                return self.queryset.filter(user=self.request.user, soon=True)
            elif search==":GUESTS":
                return self.queryset.filter(user=self.request.user, guests=True)
            elif search==":VALORATION":
                return self.queryset.filter(user=self.request.user, valoration__isnull=False)
            elif search.startswith(":LAST"):
                arr=search.split(":")
                try:
                    number=int(arr[2])
                except:
                    number=50
                return self.queryset.filter(user=self.request.user).order_by("-last")[0:number]
            else:
                self.queryset.filter(user=self.request.user)
                arr=search.split(" ")
                for word in arr:
                    self.queryset=self.queryset.filter(name__icontains=word)
                return self.queryset
        return self.queryset.filter(user=self.request.user)
    
    def list(self, request):
        return viewsets.ModelViewSet.list(self, request)

    def retrieve(self, request, *args, **kwargs):
        return viewsets.ModelViewSet.retrieve(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        models.RecipesLinks.objects.filter(recipes=instance).delete()
        models.ElaborationsProductsInThrough.objects.filter(elaborations__recipes=instance).delete()
        models.ElaborationsSteps.objects.filter(elaborations__recipes=instance).delete()
        models.Elaborations.objects.filter(recipes=instance).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class RecipesFullViewSet(#mixins.CreateModelMixin, 
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):## I leave only retrieve, not list

    queryset = models.Recipes.objects.all().prefetch_related("recipes_links", "recipes_links__type", "recipes_categories", "elaborations", 
        Prefetch("recipes_links__files",  models.Files.objects.all().only("id", "mime", "size"))
    )
    serializer_class = serializers.RecipesFullSerializer
    permission_classes = [permissions.IsAuthenticated]      
    http_method_names=['get']

    def retrieve(self, request, *args, **kwargs):
        return viewsets.ModelViewSet.retrieve(self, request, *args, **kwargs)


class RecipesCategoriesViewSet(viewsets.ModelViewSet):
    queryset = models.RecipesCategories.objects.all()
    serializer_class = serializers.RecipesCategoriesSerializer
    permission_classes = [permissions.IsAuthenticated]

class RecipesLinksViewSet(viewsets.ModelViewSet):
    queryset = models.RecipesLinks.objects.all()
    serializer_class = serializers.RecipesLinksSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, validated_data):
        return viewsets.ModelViewSet.create(self, validated_data) 

    def get_queryset(self):
        recipes=RequestGetUrl(self.request, "recipes", models.Recipes)
        if all_args_are_not_none(recipes):
            return self.queryset.filter(recipes=recipes)
        return self.queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        if instance.files is not None:
            instance.files.delete()
        instance.recipes.last=timezone.now()
        instance.recipes.save()
        return Response(status.HTTP_204_NO_CONTENT)


class RecipesLinksTypesViewSet(viewsets.ModelViewSet):
    queryset = models.RecipesLinksTypes.objects.all()
    serializer_class = serializers.RecipesLinksTypesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class StirTypesViewSet(viewsets.ModelViewSet):
    queryset = models.StirTypes.objects.all()    
    serializer_class = serializers.StirTypesSerializer
    permission_classes = [permissions.IsAuthenticated]
    
class TemperaturesTypesViewSet(viewsets.ModelViewSet):
    queryset = models.TemperaturesTypes.objects.all()    
    serializer_class = serializers.TemperaturesTypesSerializer
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
            ids=[]
            for p in self.queryset:
                if search.lower() in _(p.name).lower():
                    ids.append(p.id)
            return self.queryset.filter(id__in=ids).order_by("name")
        return self.queryset
    

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])

## Links a systemproduct to a product. No todos los system products están por eso se linka
def SystemProduct2Product(request):
    system_products=RequestUrl(request, "system_products", models.SystemProducts)
    if all_args_are_not_none(system_products):
        system_products.update_linked_product(request.user)
        return JsonResponse( True, encoder=MyDjangoJSONEncoder,     safe=False)
    return JsonResponse( False, encoder=MyDjangoJSONEncoder,     safe=False)
    


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, GroupCatalogManager ])
def Product2SystemProduct(request):
    """
    Este método solo debe ser usada por el catalog manager.
    Convierte el product en un system product, linkandolo con el nuevo system product
    
    @param request DESCRIPTION
    @type TYPE
    @return DESCRIPTION
    @rtype TYPE
    """
    product=RequestUrl(request, "product", models.Products)
    if all_args_are_not_none(product):
        if product.system_products is not None or product.elaborated_products is not None:
            return json_success_response( False, "This product can't be converted to system product")
        sp=models.SystemProducts()
        sp.name=product.name
        sp.amount=product.amount
        sp.fat=product.fat
        sp.protein=product.protein
        sp.carbohydrate=product.carbohydrate
        sp.calories=product.calories
        sp.salt=product.salt
        sp.cholesterol=product.cholesterol
        sp.sodium=product.sodium
        sp.potassium=product.potassium
        sp.fiber=product.fiber
        sp.sugars=product.sugars
        sp.saturated_fat=product.saturated_fat
        sp.ferrum=product.ferrum
        sp.magnesium=product.magnesium
        sp.phosphor=product.phosphor
        sp.glutenfree=product.glutenfree
        sp.calcium=product.calcium
        sp.food_types=product.food_types
        sp.obsolete=product.obsolete
        sp.version=timezone.now()
        
        #System company
        if product.companies==None:
            sp.system_companies=None
        else:
            if product.companies.system_companies is None: #El producto no tiene una companía del sistema
                sc=models.SystemCompanies()
                sc.name=product.companies.name
                sc.last=timezone.now()
                sc.obsolete=False
                sc.save()
            else:
                sc=product.companies.system_companies
            sp.system_companies=sc
        sp.save()
        
        #Additives
        sp.additives.set(product.additives.all())
        sp.save()
        #Systemproductsformats
                
        ## Refresh system products formats
        for f in product.productsformatsthrough_set.all():
            spft=models.SystemProductsFormatsThrough()
            spft.amount=f.amount
            spft.formats=f.formats
            spft.system_products=sp
            spft.save()
        sp.save()
            
        product.system_products=sp
        product.save()


        return json_success_response( True, "Product converted to system product")
    return json_success_response( False, "Product couldn't be converted to system product")

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, ])
## Links a systemproduct to a product. No todos los system products están por eso se linka
def SystemCompany2Company(request):
    """
        <div style="background-color:BurlyWood;">
        <p>Creates and liks a company with a system company</p>
        
        <table class="parameters table table-bordered ">
        <thead>
            <tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
        </thead>
        <tbody>
            <tr><td>system_companies<span class="label label-warning">required</span></td><td>SystemCompany url</td><td>Company will be created with this system company url</td></tr>

        </tbody>
        </table>
        </div>
    """

    system_companies=RequestUrl(request, "system_companies", models.SystemCompanies)
    if all_args_are_not_none(system_companies):
        system_companies.update_linked_company(request.user)
        return JsonResponse( True, encoder=MyDjangoJSONEncoder,     safe=False)
    return JsonResponse( False, encoder=MyDjangoJSONEncoder,     safe=False)
    

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated, ])
@transaction.atomic
def Settings(request):
    """
        get:
        Returns all user settings in a json object

        post:
        <div style="background-color:BurlyWood;">
        <p>Post user settings</p>
        
        <table class="parameters table table-bordered">
        <thead>
            <tr><th>Parameter</th><th>Type</th><th>Description</th></tr>
        </thead>
        <tbody>
            <tr><td>birthday <span class="label label-warning">required</span></td><td>Date</td><td>User birthday</td></tr>
            <tr><td>male <span class="label label-warning">required</span></td><td>Bool</td><td>True if user is a male</td></tr>
            <tr><td>last_name <span class="label label-warning">required</span></td><td>String</td><td>User last name</td></tr>
            <tr><td>first_name <span class="label label-warning">required</span></td><td>String</td><td>User first name</td></tr>
            <tr><td>email <span class="label label-warning">required</span></td><td>String</td><td>User email</td></tr>
            <tr><td>system_companies <span class="label label-warning">required</span></td><td>SystemCompany url</td><td>System company to create and link a company</td></tr>

        </tbody>
        </table>
        </div>
    """
    
    
    
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


@api_view(['POST', ])
@permission_classes([permissions.IsAuthenticated, ])
def ShoppingList(request):
    elaborations=RequestListUrl(request, "elaborations", models.Elaborations, [])
    from calories_tracker.unogenerator_files import response_report_shopping_list
    return response_report_shopping_list(request, elaborations)


@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated, ])
def Statistics(request):
    r=[]
    for name, cls in (
        (_("Activities"), models.Activities), 
        (_("Additive risks"), models.AdditiveRisks), 
        (_("Additives"), models.Additives), 
        (_("Biometrics"), models.Biometrics), 
        (_("Companies"), models.Companies), 
        (_("System companies"), models.SystemCompanies), 
        (_("Elaborated products"),  models.ElaboratedProducts), 
        (_("Elaborations"),  models.Elaborations), 
        (_("Food types"),  models.FoodTypes), 
        (_("Meals"),  models.Meals), 
        (_("Products"),  models.Products), 
        (_("Recipes"),  models.Recipes), 
        (_("System companies"), models.SystemCompanies), 
        (_("System products"),  models.SystemProducts), 
    ):
        r.append({"name": name, "value":cls.objects.all().count()})
    return JsonResponse(r, safe=False)



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
