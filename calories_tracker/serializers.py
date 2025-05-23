from base64 import b64decode
from rest_framework import serializers
#from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext as _
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from calories_tracker import models
from request_casting.request_casting import object_from_url, id_from_url


class ActivitiesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.Activities
        fields = ('url', 'id', 'name', 'description', 'multiplier', 'localname')

    @extend_schema_field(OpenApiTypes.STR)
    def get_localname(self, obj):
        return  _(obj.name)

class AdditiveRisksSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.AdditiveRisks
        fields = ('url', 'id', 'name', 'localname')

    @extend_schema_field(OpenApiTypes.STR)
    def get_localname(self, obj):
        return  _(obj.name)

class AdditivesSerializer(serializers.HyperlinkedModelSerializer):
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = models.Additives
        fields = ('url', 'id', 'name', 'description', 'additive_risks', 'fullname')
        
    @extend_schema_field(OpenApiTypes.STR)
    def get_fullname(self, o):
        return o.fullname()
        
        
class BiometricsSerializer(serializers.HyperlinkedModelSerializer):
    bmr = serializers.SerializerMethodField()
    imc = serializers.SerializerMethodField()
    imc_comment = serializers.SerializerMethodField()
    recommended_carbohydrate = serializers.SerializerMethodField()
    recommended_fat = serializers.SerializerMethodField()
    recommended_fiber = serializers.SerializerMethodField()
    recommended_protein = serializers.SerializerMethodField()
    recommended_sugars = serializers.SerializerMethodField()
    recommended_sodium = serializers.SerializerMethodField()
    class Meta:
        model = models.Biometrics
        fields = ('url', 'id', 'datetime', 'height', 'weight', 'weight_wishes', 'activities', 'bmr', 'imc', 'imc_comment', 'recommended_carbohydrate', 'recommended_fat', 'recommended_fiber', 'recommended_protein', 'recommended_sugars', 'recommended_sodium')
                
    def create(self, validated_data):
        validated_data['user']=self.context.get("request").user
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        return created
        
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_bmr(self, o):
        return o.bmr()
        
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_imc(self, o):
        return o.imc()
    @extend_schema_field(OpenApiTypes.STR)
    def get_imc_comment(self, o):
        return o.imc_comment()
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_recommended_carbohydrate(self, o):
        return o.recommended_carbohydrate()
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_recommended_fat(self, o):
        return o.recommended_fat()
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_recommended_fiber(self, o):
        return o.recommended_fiber()
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_recommended_protein(self, o):
        return o.recommended_protein()
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_recommended_sugars(self, o):
        return o.recommended_sugars()
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_recommended_sodium(self, o):
        return o.recommended_sodium()

class CompaniesSerializer(serializers.HyperlinkedModelSerializer):
    is_deletable = serializers.SerializerMethodField()
    uses=serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Companies
        fields = ('url', 'id', 'name', 'last', 'obsolete', 'uses', 'is_deletable')
        
    def create(self, validated_data):
        validated_data['user']=self.context.get("request").user
        validated_data['last']=timezone.now()
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        created.uses=0#Needed to create although is read-only
        return created

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_deletable(self, o):
        if o.uses>0:
            return False
        return True

class ElaboratedProductsProductsInThroughSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ElaboratedProductsProductsInThrough

        fields = ('id','url','products',  'amount', 'elaborated_products' )
        
class ElaboratedProductsSerializer(serializers.HyperlinkedModelSerializer):
    products_in = ElaboratedProductsProductsInThroughSerializer(many=True, read_only=True, source="elaboratedproductsproductsinthrough_set")
    calories = serializers.SerializerMethodField()
    fat = serializers.SerializerMethodField()
    protein = serializers.SerializerMethodField()
    carbohydrate = serializers.SerializerMethodField()
    salt = serializers.SerializerMethodField()
    cholesterol = serializers.SerializerMethodField()
    sodium = serializers.SerializerMethodField()
    potassium = serializers.SerializerMethodField()
    fiber = serializers.SerializerMethodField()
    sugars = serializers.SerializerMethodField()
    saturated_fat = serializers.SerializerMethodField()
    ferrum = serializers.SerializerMethodField()
    magnesium = serializers.SerializerMethodField()
    phosphor = serializers.SerializerMethodField()
    calcium = serializers.SerializerMethodField()
    glutenfree = serializers.SerializerMethodField()
    additives_risk = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = models.ElaboratedProducts
        fields = ('url', 'id', 'name', 'last', 'obsolete', 'food_types', 'final_amount', 'products_in', 'calories', 
        'fat', 'protein', 'carbohydrate', 'salt', 'cholesterol', 'sodium', 'potassium', 'fiber', 'sugars', 
        'saturated_fat', 'ferrum', 'magnesium', 'phosphor', 'calcium', 'glutenfree', 'additives_risk', "fullname",  "comment")

    def create(self, validated_data):
        data=self.context.get("request").data
        validated_data['user']=self.context.get("request").user
        validated_data['last']=timezone.now()
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        created.save()
        if "products_in" in data:
            for d in data["products_in"]:
                #Create all new
                th=models.ElaboratedProductsProductsInThrough()
                th.amount=d["amount"]
                th.products=object_from_url(d["products"], models.Products)
                th.elaborated_products=created
                th.save()
        created.save()
        created.update_associated_product()
        return created
        
         
    def update(self, instance, validated_data):
        data=self.context.get("request").data
        validated_data['user']=instance.user
        validated_data['last']=timezone.now()
        
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        updated.save()
        
        #Delete all
        qs=models.ElaboratedProductsProductsInThrough.objects.filter(elaborated_products=updated)
        if len(qs)>0:
            qs.delete()

        #Create all new
        if "products_in" in data:
            for d in data["products_in"]:
                th=models.ElaboratedProductsProductsInThrough()
                th.amount=d["amount"]
                th.products=object_from_url(d["products"], models.Products)
                th.elaborated_products=updated
                th.save()
        updated.save()
        
        updated.update_associated_product()
        return updated
        
        

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_calories(self, o):
        return o.getElaboratedProductComponent("calories")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_fat(self, o):
        return o.getElaboratedProductComponent("fat")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_protein(self, o):
        return o.getElaboratedProductComponent("protein")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_carbohydrate(self, o):
        return o.getElaboratedProductComponent("carbohydrate")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_salt(self, o):
        return o.getElaboratedProductComponent("salt")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_cholesterol(self, o):
        return o.getElaboratedProductComponent("cholesterol")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_sodium(self, o):
        return o.getElaboratedProductComponent("sodium")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_potassium(self, o):
        return o.getElaboratedProductComponent("potassium")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_fiber(self, o):
        return o.getElaboratedProductComponent("fiber")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_sugars(self, o):
        return o.getElaboratedProductComponent("sugars")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_saturated_fat(self, o):
        return o.getElaboratedProductComponent("saturated_fat")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_ferrum(self, o):
        return o.getElaboratedProductComponent("ferrum")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_magnesium(self, o):
        return o.getElaboratedProductComponent("magnesium")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_phosphor(self, o):
        return o.getElaboratedProductComponent("phosphor")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_calcium(self, o):
        return o.getElaboratedProductComponent("calcium")
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_glutenfree(self, o):
        return o.is_glutenfree()
        
    @extend_schema_field(OpenApiTypes.INT)
    def get_additives_risk(self, o):
        return o.additives_risk()

    ## For common development with products 
    @extend_schema_field(OpenApiTypes.STR)
    def get_fullname(self, o):
        return o.name


class FoodTypesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.FoodTypes
        fields = ('url', 'id', 'name', 'localname')
    @extend_schema_field(OpenApiTypes.STR)
    def get_localname(self, obj):
        return  _(obj.name)

class FilesSerializer(serializers.HyperlinkedModelSerializer):
    url_thumbnail = serializers.SerializerMethodField()
    url_content = serializers.SerializerMethodField()
    humansize=serializers.SerializerMethodField()
    extension=serializers.SerializerMethodField()
    class Meta:
        model = models.Files
        fields = ('url', 'id', 'mime', 'size', 'humansize', 'url_content', 'url_thumbnail', 'extension')
        
    def get_url_thumbnail(self, o):
        return o.url_thumbnail(self.context.get("request"))
    def get_url_content(self, o):
        return o.url_content(self.context.get("request"))
    def get_humansize(self, o):
        return o.humansize()
    def get_extension(self, o):
        return o.extension()
        

class FormatsSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.Formats
        fields = ('url', 'id', 'name', 'localname')

    @extend_schema_field(OpenApiTypes.STR)
    def get_localname(self, obj):
        return  _(obj.name)

class MealsSerializer(serializers.HyperlinkedModelSerializer):
    calories = serializers.SerializerMethodField()
    fat = serializers.SerializerMethodField()
    protein = serializers.SerializerMethodField()
    carbohydrate = serializers.SerializerMethodField()
    salt = serializers.SerializerMethodField()
    cholesterol = serializers.SerializerMethodField()
    sodium = serializers.SerializerMethodField()
    potassium = serializers.SerializerMethodField()
    fiber = serializers.SerializerMethodField()
    sugars = serializers.SerializerMethodField()
    saturated_fat = serializers.SerializerMethodField()
    ferrum = serializers.SerializerMethodField()
    magnesium = serializers.SerializerMethodField()
    phosphor = serializers.SerializerMethodField()
    calcium = serializers.SerializerMethodField()
    glutenfree = serializers.SerializerMethodField()
    class Meta:
        model = models.Meals
        fields = ('url', 'id', 'datetime', 'products', 'amount', 'calories', 
        'fat', 'protein', 'carbohydrate', 'salt', 'cholesterol', 'sodium', 'potassium', 'fiber', 'sugars', 
        'saturated_fat', 'ferrum', 'magnesium', 'phosphor', 'calcium', 'glutenfree')       

    def create(self, validated_data):
        validated_data['user']=self.context.get("request").user
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        return created
        
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_calories(self, o):
        return o.getProductComponent("calories", 0)
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_fat(self, o):
        return o.getProductComponent("fat")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_protein(self, o):
        return o.getProductComponent("protein")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_carbohydrate(self, o):
        return o.getProductComponent("carbohydrate")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_salt(self, o):
        return o.getProductComponent("salt")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_cholesterol(self, o):
        return o.getProductComponent("cholesterol")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_sodium(self, o):
        return o.getProductComponent("sodium")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_potassium(self, o):
        return o.getProductComponent("potassium")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_fiber(self, o):
        return o.getProductComponent("fiber")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_sugars(self, o):
        return o.getProductComponent("sugars")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_saturated_fat(self, o):
        return o.getProductComponent("saturated_fat")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_ferrum(self, o):
        return o.getProductComponent("ferrum")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_magnesium(self, o):
        return o.getProductComponent("magnesium")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_phosphor(self, o):
        return o.getProductComponent("phosphor")
    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_calcium(self, o):
        return o.getProductComponent("calcium")
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_glutenfree(self, o):
        return o.products.glutenfree
    





class PillEventsSerializer(serializers.HyperlinkedModelSerializer):
    is_taken= serializers.SerializerMethodField()
    class Meta:
        model = models.PillEvents
        fields = ('url', 'id', 'pillname', 'dt', 'dt_intake', 'highlight_late', 'is_taken')
    
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_taken(self, obj):
        return  obj.is_taken()

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data['user']=request.user
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        return created
        
         
    def update(self, instance, validated_data):
        validated_data['user']=instance.user
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        return updated


class PotsSerializer(serializers.HyperlinkedModelSerializer):
    fullname = serializers.SerializerMethodField()
    volume = serializers.SerializerMethodField()
    photo=FilesSerializer(read_only=True)
    class Meta:
        model = models.Pots
        fields = ('url', 'id', 'name', 'fullname', 'diameter', 'weight', 'height', 'volume', 'photo')

    @extend_schema_field(OpenApiTypes.STR)
    def get_fullname(self, obj):
        return  _(obj.fullname())

    @extend_schema_field(OpenApiTypes.FLOAT)
    def get_volume(self, obj):
        return  obj.volume()

    def create(self, validated_data):
        request=self.context.get("request")
        validated_data['user']=request.user
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        if 'photo_content' in request.data and request.data['photo_content'] is not None:
            f=models.Files()
            f.content=b64decode(request.data['photo_content'].encode('utf-8'))
            f.size=len(f.content)
            f.mime=request.data["photo_mime"]
            f.user=request.user
            f.save()
            created.photo=f
        created.save()
        return created

    def update(self, instance, validated_data):
        request=self.context.get("request")
        validated_data['user']=self.context.get("request").user
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        if 'photo_content' in request.data and request.data['photo_content'] is not None:# There is photo data
            if instance.photo is None:
                f=models.Files()
            else:
                f=instance.photo
            f.thumbnail=None #Erases old thumbnail
            f.content=b64decode(request.data['photo_content'].encode('utf-8'))
            f.size=len(f.content)
            f.mime=request.data["photo_mime"]
            f.user=request.user
            f.save()
            updated.photo=f
        updated.save()
        return updated

class ProductsFormatsThroughSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ProductsFormatsThrough

        fields = ('amount', 'formats')
        
class ProductsSerializer(serializers.HyperlinkedModelSerializer):
    formats= ProductsFormatsThroughSerializer(many=True, read_only=True, source="productsformatsthrough_set")
    uses = serializers.IntegerField(read_only=True)
    fullname = serializers.SerializerMethodField()
    additives_risk = serializers.SerializerMethodField()
    

    is_deletable = serializers.SerializerMethodField()
    is_editable = serializers.SerializerMethodField()

    class Meta:
        model = models.Products
        fields = ('url', 'id', 'additives', 'amount', 'calcium', 'calories','carbohydrate', 'cholesterol', 'companies', 'elaborated_products', 
            'fat', 'ferrum', 'fiber', 'food_types', 'formats', 'glutenfree', 'magnesium', 'name', 'obsolete', 'phosphor', 'potassium', 
            'protein', 'salt', 'saturated_fat', 'sodium', 'sugars', 'version', 'version_description', 'version_parent', 'openfoodfacts_id', 
            'fullname', 'uses', 'is_editable', 'is_deletable', 'additives_risk','density'
        )
        
    def create(self, validated_data):
        data=self.context.get("request").data
        validated_data['user']=self.context.get("request").user
        validated_data['version']=timezone.now()
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        created.save()
        if "formats" in data:
            for d in data["formats"]:
                #Create all new
                th=models.ProductsFormatsThrough()
                th.amount=d["amount"]
                th.formats=object_from_url(d["formats"], models.Formats)
                th.products=created
                th.save()
        created.save()
        
        created.uses=0#Needed to create although is read-only
        return created
        
         
    def update(self, instance, validated_data):
        data=self.context.get("request").data
        validated_data['user']=self.context.get("request").user
        validated_data['version']=timezone.now()
        
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        updated.save()
        
        #Delete all
        qs=models.ProductsFormatsThrough.objects.filter(products=updated)
        if len(qs)>0:
            qs.delete()

        #Create all new
        if "formats" in data:
            for d in data["formats"]:
                th=models.ProductsFormatsThrough()
                th.amount=d["amount"]
                th.formats=object_from_url(d["formats"], models.Formats)
                th.products=updated
                th.save()
        updated.save()
        
        return updated
        
    @extend_schema_field(OpenApiTypes.STR)
    def get_fullname(self, o):
        return o.fullname()
        
    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_deletable(self, o):
        """
            Uses is an annotation in view set, so if I want to serialize an item I need to calculate them object by object
        """
        if hasattr(o, "uses"):
            uses=o.uses
        else:
            uses=o.getUses()
        if uses>0:
            return False
        return True

    @extend_schema_field(OpenApiTypes.BOOL)
    def get_is_editable(self, o):
        if o.elaborated_products is not None:
            return False
        return True
        
    @extend_schema_field(OpenApiTypes.INT)
    def get_additives_risk(self, o):
        return o.additives_risk()


class WeightWishesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.WeightWishes
        fields = ('url', 'id', 'name', 'localname')

    @extend_schema_field(OpenApiTypes.STR)
    def get_localname(self, obj):
        return  _(obj.name)
        
class RecipesCategoriesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.RecipesCategories
        fields = ('url', 'id', 'name', 'localname')

    @extend_schema_field(OpenApiTypes.STR)
    def get_localname(self, obj):
        return  _(obj.name)

class RecipesLinksSerializer(serializers.HyperlinkedModelSerializer):
    files=FilesSerializer(read_only=True)

    class Meta:
        model = models.RecipesLinks
        fields = ('url', 'id', 'description', 'type', 'link', 'recipes', 'files')
        
    def create(self, validated_data):
        request = self.context.get("request")
        ## Converts base 64 string to  bytes
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        
        
        if "content" in request.data and request.data['content'] is not None:
            f=models.Files()
            f.content=b64decode(request.data['content'].encode('utf-8'))
            f.size=len(f.content)
            f.mime=request.data["mime"]
            f.user=request.user
            f.save()
            created.files=f
        created.save()
        created.recipes.last=timezone.now()
        created.recipes.save()
        return created
    
    ## Update doesn't update blob, only changes metadata
    def update(self, instance, validated_data):
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        updated.recipes.last=timezone.now()
        updated.recipes.save()
        return updated

class ElaborationsProductsInThroughSerializer(serializers.HyperlinkedModelSerializer):
    final_grams = serializers.SerializerMethodField()
    fullname = serializers.SerializerMethodField()
    class Meta:
        model = models.ElaborationsProductsInThrough
        fields = ('url', 'id','products', 'measures_types', 'amount', 'elaborations' , 'final_grams', 'fullname', 'comment', 'ni', 'automatic_percentage')
        
        
    def create(self, validated_data):
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        created.elaborations.recipes.last=timezone.now()
        created.elaborations.recipes.save()
        return created
    
    ## Update doesn't update blob, only changes metadata
    def update(self, instance, validated_data):
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        updated.elaborations.recipes.last=timezone.now()
        updated.elaborations.recipes.save()
        return updated

        
    @extend_schema_field(OpenApiTypes.DECIMAL)
    def get_final_grams(self, obj):
        return  obj.final_grams()
        
    @extend_schema_field(OpenApiTypes.STR)
    def get_fullname(self, obj):
        return obj.fullname()

class ElaborationsContainersSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ElaborationsContainers
        fields = ('url', 'id',  'name','elaborations')

class ElaborationsExperiencesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ElaborationsExperiences
        fields = ('url', 'id',  'datetime', 'experience', 'elaborations')

class ElaborationsTextsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ElaborationsTexts
        fields = ( 'url',   'text', )
        
            
    def create(self, validated_data):
        """
            This method require elaborations_id as parameter in post method
        """
        request = self.context.get("request")
#        try:
        elaborations=models.Elaborations.objects.get(pk=id_from_url(request.data["elaborations"]), recipes__user=request.user)
#        except:
#               raise ValidationError("Elaboration doesn't exist")
        created=models.ElaborationsTexts()
        created.elaborations=elaborations
        created.text=validated_data["text"]
        created.save()
        created.elaborations.recipes.last=timezone.now()
        created.elaborations.recipes.save()
        return created
        
         
    def update(self, instance, validated_data):
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        updated.save()
        
        updated.elaborations.recipes.last=timezone.now()
        updated.elaborations.recipes.save()
        return updated

class ElaborationsSerializer(serializers.HyperlinkedModelSerializer):
    elaborations_products_in = ElaborationsProductsInThroughSerializer(many=True, read_only=True, source="elaborationsproductsinthrough_set")
    elaborations_containers=ElaborationsContainersSerializer(many=True, read_only=True)
    elaborations_experiences=ElaborationsExperiencesSerializer(many=True, read_only=True)
    elaborations_texts=ElaborationsTextsSerializer(many=False, read_only=True)
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = models.Elaborations
        fields = ('url', 'id', 'diners', 'final_amount', 'fullname', 'recipes', 'elaborations_products_in', 
        'elaborations_containers', 'elaborations_experiences',  'automatic', 'automatic_adaptation_step', 'elaborations_texts')
        
    def create(self, validated_data):
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        created.save()
        created.recipes.last=timezone.now()
        created.recipes.save()
        return created

    def update(self, instance, validated_data):
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        updated.save()
        
        updated.recipes.last=timezone.now()
        updated.recipes.save()
        return updated
   
    def get_fullname(self, o):
        return o.fullname()

class RecipesSerializer(serializers.HyperlinkedModelSerializer):
    recipes_links=RecipesLinksSerializer(many=True, read_only=True)
    elaborations= ElaborationsSerializer( many=True, read_only=True)
    class Meta:
        model = models.Recipes
        fields = ('url', 'id', 'name', 'last', 'datetime', 'obsolete', 'food_types',   'comment', 'valoration', 'guests', 'soon', 'recipes_categories', 'recipes_links', 'elaborations')
        

    def create(self, validated_data):
        request = self.context.get("request")
        validated_data['datetime']=timezone.now()
        validated_data['user']=request.user
        validated_data['last']=timezone.now()
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        return created
        
         
    def update(self, instance, validated_data):
        validated_data["datetime"]=instance.datetime
        validated_data['user']=instance.user
        validated_data['last']=timezone.now()
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        return updated

class RecipesLinksTypesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.RecipesLinksTypes
        fields = ('url', 'id', 'name', 'localname')

    @extend_schema_field(OpenApiTypes.STR)
    def get_localname(self, obj):
        return  _(obj.name)        

class MeasuresTypesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.MeasuresTypes
        fields = ('url', 'id', 'name', 'localname')

    @extend_schema_field(OpenApiTypes.STR)
    def get_localname(self, obj):
        return  _(obj.name)

