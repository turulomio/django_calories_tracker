from calories_tracker import serializers, models,  commons
from calories_tracker.reusing.connection_dj import show_queries, show_queries_function
from calories_tracker.reusing.decorators import ptimeit
from pydicts.casts import dtaware2str
from calories_tracker.paginators import PagePaginationWithTotalPages, vtabledata_options2orderby
from calories_tracker.permissions import GroupCatalogManager
from request_casting.request_casting import all_args_are_not_none, RequestUrl, RequestString, RequestDate, RequestBool, RequestListOfUrls, RequestInteger, RequestDtaware
from pydicts.myjsonencoder import MyJSONEncoderDecimalsAsFloat
from dateutil.rrule import rrule, DAILY, HOURLY
from decimal import Decimal
from django.db import transaction
from django.db.models import Count, Min, Prefetch, Sum
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from drf_spectacular.types import OpenApiTypes
from pydicts import lod
from rest_framework import viewsets, permissions,  status, mixins
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from statistics import median

ptimeit
show_queries
show_queries_function


@permission_classes([permissions.IsAuthenticated, ])
@api_view(['GET', ])
def CatalogManager(request):
    return JsonResponse( request.user.groups.filter(name="CatalogManager").exists(), encoder=MyJSONEncoderDecimalsAsFloat, safe=False)


class CatalogModelViewSet(viewsets.ModelViewSet):
    def get_permissions(self):    
        """
            Overrides get_permissions to set GroupCatalogManager permission for CRUD actions
            Only list and get actions authenticated, ther rest for GroupCatalogManager.
        """
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            self.permission_classes = [permissions.IsAuthenticated, GroupCatalogManager]
        else:# get and custome actions
            self.permission_classes = [permissions.IsAuthenticated]
        return viewsets.ModelViewSet.get_permissions(self)

@api_view(['GET', ])
@permission_classes([permissions.IsAuthenticated, ])
def Time(request):
    return JsonResponse( timezone.now(), encoder=MyJSONEncoderDecimalsAsFloat, safe=False)
    
    
class WeightWishesViewSet(CatalogModelViewSet):
    queryset = models.WeightWishes.objects.all()
    serializer_class = serializers.WeightWishesSerializer

class ActivitiesViewSet(CatalogModelViewSet):
    queryset = models.Activities.objects.all()
    serializer_class = serializers.ActivitiesSerializer

class AdditiveRisksViewSet(CatalogModelViewSet):
    queryset = models.AdditiveRisks.objects.all()
    serializer_class = serializers.AdditiveRisksSerializer

class AdditivesViewSet(CatalogModelViewSet):
    queryset = models.Additives.objects.all()
    serializer_class = serializers.AdditivesSerializer

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
        day=RequestDate(self.request, "day")
        if all_args_are_not_none(day):        
            return models.Biometrics.objects.select_related("user").select_related("user__profiles").select_related("activities").filter(user=self.request.user, datetime__date__lte=day).order_by("-datetime")[:1]
        return models.Biometrics.objects.select_related("user").select_related("user__profiles").select_related("activities").filter(user=self.request.user).order_by("datetime")

class CompaniesViewSet(viewsets.ModelViewSet):
    queryset = models.Companies.objects.all()
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
        deleted_elaborated_product=models.ElaboratedProducts.hurl(request, instance.id)
        qs_products_in=models.ElaboratedProductsProductsInThrough.objects.filter(elaborated_products=instance)
        qs_products_in.delete()
        #Destroy asoociated product
        qs=models.Products.objects.filter(elaborated_products=instance  )
        deleted_product=None
        if len(qs)>0:
            deleted_product=models.Products.hurl(request, qs[0].id)
            qs[0].delete()
        self.perform_destroy(instance)
        #Returns url deleted elaborated_product and asociated_product
        r={"deleted_elaborated_product": deleted_elaborated_product,  "deleted_product":deleted_product}
        return JsonResponse(r, status=status.HTTP_200_OK)
    
    
class ElaboratedProductsProductsInThroughViewSet(viewsets.ModelViewSet):
    queryset = models.ElaboratedProductsProductsInThrough.objects.all()
    serializer_class = serializers.ElaboratedProductsProductsInThroughSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        elaborated_products=RequestUrl(self.request, "elaborated_products", models.ElaboratedProducts)
        #products=RequestUrl(self.request, "products", models.Products)
        if all_args_are_not_none(elaborated_products):        
            return self.queryset.filter(elaborated_products=elaborated_products, elaborated_products__user=self.request.user)
        return self.queryset.filter(elaborated_products__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.elaborated_products.last=timezone.now()
        instance.elaborated_products.save()
        return viewsets.ModelViewSet.destroy(self, request, args, kwargs)

class ElaborationsViewSet(viewsets.ModelViewSet):
    queryset = models.Elaborations.objects.all().select_related("recipes")
    serializer_class = serializers.ElaborationsSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
    def get_queryset(self):
        recipes=RequestUrl(self.request, "recipes", models.Recipes)
        if all_args_are_not_none(recipes):
            return self.queryset.filter(recipes=recipes, recipes__user=self.request.user)
        return self.queryset.filter(recipes__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        models.ElaborationsProductsInThrough.objects.filter(elaborations=instance).delete()
        instance.recipes.last=timezone.now()
        instance.recipes.save()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


    @action(detail=True, methods=['POST'], name='It creates and elaborated product from a recipe elaboration', url_path="create_elaborated_product", url_name='create_elaborated_product', permission_classes=[permissions.IsAuthenticated])
    def create_elaborated_product(self, request, pk=None):
        elaboration = self.get_object()
#        #Sets all elaborated products and products from this recipe obsolete
#        for ep in models.ElaboratedProducts.objects.filter(name=elaboration.recipes.name):
#            ep.obsolete=True
#            ep.save()
#            models.Products.objects.filter(elaborated_products=ep).update(obsolete=True)
        #Creates a new elaborated product
        ep=models.ElaboratedProducts()
        ep.last=timezone.now()
        dt_string=dtaware2str(ep.last, "%Y-%m-%d %H:%M:%S")
        ep.name=_("{0} for {1} diners ({2})").format(elaboration.recipes.name, elaboration.diners, dt_string )
        ep.final_amount=elaboration.final_amount
        ep.food_types=elaboration.recipes.food_types
        ep.obsolete=False
        ep.user=request.user
        ep.comment=_("This elaborated product was created from '{0}' recipe for {1} diners ({2}).").format(elaboration.recipes.name, elaboration.diners, dt_string)
        ep.save()
        #Adds all products_in
        for rpi in elaboration.elaborationsproductsinthrough_set.all():
            epi=models.ElaboratedProductsProductsInThrough()
            epi.amount=rpi.final_grams()
            epi.products=rpi.products
            epi.elaborated_products=ep
            epi.save()
        #Creates asociated product
        product_associated=ep.update_associated_product()
        r={
            "elaborated_product":serializers.ElaboratedProductsSerializer(ep, context={'request': request}).data, 
            "product": serializers.ProductsSerializer(product_associated, context={'request': request}).data
        }
        #Returns created elaborated product serialized
        return JsonResponse(r, status=status.HTTP_200_OK)
        
    @action(detail=True, methods=['POST'], name='Create a new automatic elaboration', url_path="create_automatic_elaboration", url_name='create_automatic_elaboration', permission_classes=[permissions.IsAuthenticated])
    @transaction.atomic
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
            new.automatic_adaptation_step=old.automatic_adaptation_step
            new.save()
            
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
                new_pi.automatic_parent=old_pi
                new_pi.save()
            new.save()
            
            for old_container in old.elaborations_containers.all():
                new_container=models.ElaborationsContainers()
                new_container.name=old_container.name
                new_container.elaborations=new
                new_container.save()
                
            #elaborations_text
            new.elaborations_texts=models.ElaborationsTexts()
            new.elaborations_texts.elaborations=new
            if hasattr(old, "elaborations_texts"):
                new.elaborations_texts.text=models.ElaborationsTexts.generate_automatic_text(new, old.elaborations_texts.text)
            new.elaborations_texts.save()
        
              
            return JsonResponse(serializers.ElaborationsSerializer(new, context={'request': request}).data, status=status.HTTP_200_OK)
        return Response({"detail": "Error creating automatic elaboration"}, status=status.HTTP_400_BAD_REQUEST)

class ElaborationsContainersViewSet(viewsets.ModelViewSet):
    queryset = models.ElaborationsContainers.objects.all()
    serializer_class = serializers.ElaborationsContainersSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        elaboration=RequestUrl(self.request, "elaboration", models.Elaborations)
        if all_args_are_not_none(elaboration):        
            return self.queryset.filter(elaborations=elaboration, elaborations__recipes__user=self.request.user)
        return self.queryset.filter(elaborations__recipes__user=self.request.user)

class ElaborationsExperiencesViewSet(viewsets.ModelViewSet):
    queryset = models.ElaborationsExperiences.objects.all()
    serializer_class = serializers.ElaborationsExperiencesSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        elaboration=RequestUrl(self.request, "elaboration", models.Elaborations)
        if all_args_are_not_none(elaboration):        
            return self.queryset.filter(elaborations=elaboration, elaborations__recipes__user=self.request.user)
        return self.queryset.filter(elaborations__recipes__user=self.request.user)
        
class ElaborationsTextsViewSet(viewsets.ModelViewSet):
    queryset = models.ElaborationsTexts.objects.all()
    serializer_class = serializers.ElaborationsTextsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        elaboration=RequestUrl(self.request, "elaboration", models.Elaborations)
        if all_args_are_not_none(elaboration):        
            return self.queryset.filter(elaborations=elaboration, elaborations__recipes__user=self.request.user)
        return self.queryset.filter(elaborations__recipes__user=self.request.user)

class ElaborationsProductsInThroughViewSet(viewsets.ModelViewSet):
    queryset = models.ElaborationsProductsInThrough.objects.all()
    serializer_class = serializers.ElaborationsProductsInThroughSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        elaboration=RequestUrl(self.request, "elaboration", models.Elaborations)
        if all_args_are_not_none(elaboration):        
            return self.queryset.filter(elaborations=elaboration, elaborations__recipes__user=self.request.user)
        return self.queryset.filter(elaborations__recipes__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.elaborations.recipes.last=timezone.now()
        instance.elaborations.recipes.save()
        return viewsets.ModelViewSet.destroy(self, request, args, kwargs)

class FoodTypesViewSet(CatalogModelViewSet):
    queryset = models.FoodTypes.objects.all()
    serializer_class = serializers.FoodTypesSerializer

class FormatsViewSet(CatalogModelViewSet):
    queryset = models.Formats.objects.all()
    serializer_class = serializers.FormatsSerializer
    
class MeasuresTypesViewSet(CatalogModelViewSet):
    queryset = models.MeasuresTypes.objects.all()
    serializer_class = serializers.MeasuresTypesSerializer

class MealsViewSet(viewsets.ModelViewSet):
    queryset = models.Meals.objects.all()
    serializer_class = serializers.MealsSerializer
    permission_classes = [permissions.IsAuthenticated]      

    ## api/formats/product=url. Search all formats of a product
    def get_queryset(self):
        day=RequestDate(self.request, 'day') 
        if all_args_are_not_none(day):
            return models.Meals.objects.filter(user=self.request.user, datetime__date=day).order_by("datetime")
        return self.queryset.filter(user=self.request.user)

    ## delete_several. meals as an array
    @extend_schema(
        parameters=[
            OpenApiParameter(name='meals', description='Meal to delete (List)', required=True, type=OpenApiTypes.URI), 
        ],
    )
    @action(detail=False, methods=['post'])
    def delete_several(self, request):
        meals=RequestListOfUrls(request, "meals", models.Meals)
        if all_args_are_not_none(meals):
            for meal in meals:
                meal.delete()
            return Response({"detail":'Meals.delete_several success'}, status=status.HTTP_200_OK)
        return Response({"detail": 'Meals.delete_several failure'}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=["get"], name='Shows user meals ranking', url_path="ranking", url_name='ranking', permission_classes=[permissions.IsAuthenticated])
    def ranking(self, request):
        from_date=RequestDate(request, "from_date")
        qs_meals=models.Meals.objects.select_related("products").filter(user=request.user)
        if from_date is not None:
            qs_meals=qs_meals.filter(datetime__date__gte=from_date)

        lod_=list(qs_meals.values("products__id").annotate(amount=Sum("amount")).order_by("-amount"))
        lod.lod_calculate(lod_, "products",  lambda d, index: models.Products.hurl(request, d["products__id"]))
        lod.lod_calculate(lod_, "ranking",  lambda d, index: index+1)
        lod.lod_remove_key(lod_, "products__id")

        return Response(lod_, status=status.HTTP_200_OK)
        
class PillEventsViewSet(viewsets.ModelViewSet):
    queryset = models.PillEvents.objects.all()
    serializer_class = serializers.PillEventsSerializer
    permission_classes = [permissions.IsAuthenticated]      
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def list(self, request):
        year=RequestInteger(self.request, 'year') 
        month=RequestInteger(self.request, 'month') 
        if all_args_are_not_none(year, month):
            queryset= self.get_queryset().filter(dt__year=year, dt__month=month)
            serializer=self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(_("You need to set year and month parameters"), status=status.HTTP_400_BAD_REQUEST)
    

    @action(detail=False, methods=['POST'], name='Set pillevents each day at an hour', url_path="set_each_day", url_name='set_each_day', permission_classes=[permissions.IsAuthenticated, ])
    @transaction.atomic
    def set_each_day(self, request, pk=None):
        """
            It uses hour from dt_from to set hour each day
        """
        pillname=RequestString(request, "pillname")
        dt_from=RequestDtaware(request,  "dt_from", models.get_profile(request.user).get_timezone())
        days=RequestInteger(request,  "days")
    
        if all_args_are_not_none(pillname, dt_from, days):
            r=[]
            for dt in rrule(DAILY, dtstart=dt_from, count=days):
                pe=models.PillEvents()
                pe.user=request.user
                pe.pillname=pillname
                pe.dt=dt
                pe.dt_intake=None
                pe.save()
                r.append(pe)
            return Response(serializers.PillEventsSerializer(r, many=True,  context={'request': request}).data, status=status.HTTP_200_OK)
        else:
            return Response(_("Something was wrong setting pill events each day"), status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['POST'], name='Set pillevents each n hours', url_path="set_each_n_hours", url_name='set_each_n_hours', permission_classes=[permissions.IsAuthenticated, ])
    @transaction.atomic
    def set_each_n_hours(self, request, pk=None):
        """
            It uses hour from dt_from to set hour each day
        """
        pillname=RequestString(request, "pillname")
        dt_from=RequestDtaware(request,  "dt_from", models.get_profile(request.user).get_timezone())
        hours=RequestInteger(request,  "hours")
        number=RequestInteger(request,  "number")
        if all_args_are_not_none(pillname, dt_from, hours, number):
            r=[]
            for dt in rrule(HOURLY, dtstart=dt_from, interval=hours,  count=number):
                pe=models.PillEvents()
                pe.user=request.user
                pe.pillname=pillname
                pe.dt=dt
                pe.dt_intake=None
                pe.save()
                r.append(pe)
            return Response(serializers.PillEventsSerializer(r, many=True,  context={'request': request}).data, status=status.HTTP_200_OK)
        else:
            return Response(_("Something was wrong setting pill events each n hours"), status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=False, methods=['POST'], name='Deletes pillevents from a pillname and a datetime', url_path="delete_from_dt", url_name='delete_from_dt', permission_classes=[permissions.IsAuthenticated, ])
    def delete_from_dt(self, request, pk=None):
        """
            It uses hour from dt_from to set hour each day
        """
        pillname=RequestString(request, "pillname")
        dt_from=RequestDtaware(request,  "dt_from", models.get_profile(request.user).get_timezone())
    
        if all_args_are_not_none(pillname, dt_from):
            deleted=models.PillEvents.objects.filter(user=request.user, pillname=pillname,  dt__gte=dt_from).delete()
            return Response(deleted, status=status.HTTP_200_OK)
        else:
            return Response(_("Something was wrong deleting pill events from dt"), status=status.HTTP_400_BAD_REQUEST)
    
    
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
    
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        if instance.photo is not None:
            instance.photo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductsViewSet(viewsets.ModelViewSet):
    queryset = models.Products.objects.all()
    serializer_class = serializers.ProductsSerializer
    permission_classes = [permissions.IsAuthenticated]      
    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)\
            .select_related("companies",  "elaborated_products", )\
            .prefetch_related("additives", "additives__additive_risks","productsformatsthrough_set")\
            .annotate(uses=Count("meals", distinct=True)+Count("elaboratedproductsproductsinthrough", distinct=True) + Count("elaborationsproductsinthrough", distinct=True)).order_by("name")
    def list(self, request):
        r=viewsets.ModelViewSet.list(self, request)
        return r

    @action(detail=True, methods=['GET'], name='Returns data from both products to valorate a data transfer', url_path="get_data_transfer", url_name='get_data_transfer', permission_classes=[permissions.IsAuthenticated])
    def get_data_transfer(self, request, pk=None):
        product_from=self.get_object()
        product_to=RequestUrl(request, "product_to", models.Products)
    
        if all_args_are_not_none(product_from, product_to):
            r=[]
            for p in (product_from, product_to):
                r.append({
                    "product": request.build_absolute_uri(reverse('products-detail', args=(p.id, ))), 
                    "products_in": models.ElaboratedProductsProductsInThrough.objects.filter(products=p).count(), 
                    "meals": models.Meals.objects.filter(products=p).count(),
                })
            return JsonResponse( r, encoder=MyJSONEncoderDecimalsAsFloat, safe=False)

    @action(detail=True, methods=['POST'], name='Transfers data from a product to other', url_path="data_transfer", url_name='data_transfer', permission_classes=[permissions.IsAuthenticated, GroupCatalogManager])
    def data_transfer(self, request, pk=None):
        product_from=self.get_object()
        product_to=RequestUrl(request, "product_to", models.Products)
    
        if all_args_are_not_none(product_from, product_to):
            for pi in models.ElaboratedProductsProductsInThrough.objects.filter(products=product_from):
                pi.products=product_to
                pi.save()
            for m in models.Meals.objects.filter(products=product_from):
                m.products=product_to
                m.save()            
            return JsonResponse( True, encoder=MyJSONEncoderDecimalsAsFloat, safe=False)


    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        models.ProductsFormatsThrough.objects.filter(products=instance).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

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
    pagination_class=PagePaginationWithTotalPages
    @extend_schema(
        parameters=[
            OpenApiParameter(name='search', description='String used to search recipes. ', required=True, type=str), 
        ],
    )
    def get_queryset(self):

        return self.queryset.filter(user=self.request.user)
    
    def list(self, request):
        search=RequestString(self.request, 'search') 
        if all_args_are_not_none(search):
            if search==":SOON":
                self.queryset= self.queryset.filter(user=self.request.user, soon=True)
            elif search==":GUESTS":
                self.queryset= self.queryset.filter(user=self.request.user, guests=True)
            elif search==":VALORATION":
                self.order_by="-valoration"
                self.queryset= self.queryset.filter(user=self.request.user, valoration__isnull=False)
            elif search==":WITH_ELABORATIONS":
                recipes_ids=list(models.Elaborations.objects.filter(recipes__user=self.request.user).values_list("recipes__id", flat=True))
                self.queryset= self.queryset.filter(pk__in=recipes_ids, user=self.request.user)
            elif search.startswith(":WITHOUT_MAINPHOTO"):
                recipes_with_photo_ids=list(models.RecipesLinks.objects.filter(type_id=models.eRecipeLink.MainPhoto).filter(recipes__user=self.request.user).values_list("recipes__id", flat=True))
                self.queryset= self.queryset.exclude(pk__in=recipes_with_photo_ids).filter(user=self.request.user)
            elif search.startswith(":LAST"):
                self.queryset= self.queryset.filter(user=self.request.user)
            elif search.startswith(":INGREDIENTS "): #:INGREDIENTS 1, 2, 3, 4
                try:
                    products_ids=commons.string2list_of_integers(search.replace(":INGREDIENTS ", ""), ",")
                    qs=self.queryset
                    for product_id in products_ids:
                        qs=qs.filter(elaborations__elaborationsproductsinthrough__products__id=product_id)
                    self.queryset= qs.distinct()
                except:
                    print("Error parsing ingredients")
                    self.queryset= self.queryset.none()
            else:
                self.queryset.filter(user=self.request.user)
                arr=search.split(" ")
                for word in arr:
                    self.queryset=self.queryset.filter(name__icontains=word)
                self.queryset= self.queryset
        
        
        
        order_by=vtabledata_options2orderby(self.request, "-last")
        page = self.paginate_queryset(self.queryset.order_by(*order_by))
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def retrieve(self, request, *args, **kwargs):
        return viewsets.ModelViewSet.retrieve(self, request, *args, **kwargs)

    @transaction.atomic
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        models.RecipesLinks.objects.filter(recipes=instance).delete()
        models.ElaborationsProductsInThrough.objects.filter(elaborations__recipes=instance).delete()
        models.Elaborations.objects.filter(recipes=instance).delete()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
    @extend_schema(
        description="""
            Merge several recipes (Post parameters) to the selected in main url
        """
    )
    @action(detail=True, methods=['POST'], name='Merge several recipes into this recipe', url_path="merge", url_name='merge', permission_classes=[permissions.IsAuthenticated])
    def merge(self, request, pk=None):
        main_recipe=self.get_object()
        recipes=RequestListOfUrls(request, "recipes", models.Recipes, validate_object=lambda o: o.user==request.user)
        if all_args_are_not_none(recipes):
            if main_recipe in recipes:
                return Response(_("You should not pass the recipe that will remain in the list of recipes to be merged"), status=status.HTTP_400_BAD_REQUEST)
            models.RecipesLinks.objects.filter(recipes__in=recipes).update(recipes=main_recipe)
            models.Elaborations.objects.filter(recipes__in=recipes).update(recipes=main_recipe)
            models.Recipes.objects.filter(id__in=[recipe.id for recipe in recipes]).delete()
            recipes=models.Recipes.objects.get(pk=main_recipe.id)
            return Response(serializers.RecipesSerializer(recipes, context={'request': request}).data, status=status.HTTP_200_OK)
        return Response(_("Something was wrong with your merge urls"), status=status.HTTP_400_BAD_REQUEST)

class RecipesCategoriesViewSet(CatalogModelViewSet):
    queryset = models.RecipesCategories.objects.all()
    serializer_class = serializers.RecipesCategoriesSerializer

class RecipesLinksViewSet(viewsets.ModelViewSet):
    queryset = models.RecipesLinks.objects.all()
    serializer_class = serializers.RecipesLinksSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        recipes=RequestUrl(self.request, "recipes", models.Recipes)
        if all_args_are_not_none(recipes):
            return self.queryset.filter(recipes=recipes, recipes__user=self.request.user)
        return self.queryset.filter(recipes__user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        if instance.files is not None:
            instance.files.delete()
        instance.recipes.last=timezone.now()
        instance.recipes.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RecipesLinksTypesViewSet(CatalogModelViewSet):
    queryset = models.RecipesLinksTypes.objects.all()
    serializer_class = serializers.RecipesLinksTypesSerializer

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
        return JsonResponse( r, encoder=MyJSONEncoderDecimalsAsFloat,     safe=False)
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
            
            # Prepare Response
            r={}
            r['first_name']=request.user.first_name
            r['last_name']=request.user.last_name
            r['last_login']=request.user.last_login     
            r['email']=request.user.email     
            r['birthday']=p.birthday
            r['male']=p.male
            
            return JsonResponse( r, encoder=MyJSONEncoderDecimalsAsFloat,     safe=False)
        return Response(status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', ])
@permission_classes([permissions.IsAuthenticated, ])
def ShoppingList(request):
    elaborations=RequestListOfUrls(request, "elaborations", models.Elaborations, [])
    #Elaborations must check if elaborations are of request.user due to requestlisturl make a fast queryset
    for e in elaborations:
        if e.recipes.user!=request.user:
            return Response({"detail":"Some elaborations are not of current user"},  status=status.HTTP_400_BAD_REQUEST)
            
        r={}
        r["recipes"]=[]
        for e in elaborations:
            r["recipes"].append(e.fullname())
            
        ## Generate a dictionary with p as key
        list={}
        for e in elaborations:
            for i in e.elaborationsproductsinthrough_set.all().select_related("products__companies", "measures_types"):
                if not i.products in list:
                    list[i.products]=0
                list[i.products]=list[i.products]+i.final_grams()

        r["shopping_list"]=[]
        for k, v in list.items():            
            r["shopping_list"].append({"grams": int(v), "product_fullname":k.fullname()})
    return Response(r)


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
        (_("Elaborated products"),  models.ElaboratedProducts), 
        (_("Elaborations"),  models.Elaborations), 
        (_("Food types"),  models.FoodTypes), 
        (_("Meals"),  models.Meals), 
        (_("Products"),  models.Products), 
        (_("Recipes"),  models.Recipes), 
    ):
        r.append({"name": name, "value":cls.objects.all().count()})
    return JsonResponse(r, safe=False)

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
    if len(qs_products)>0:
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
        if sel_m is not None:
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


