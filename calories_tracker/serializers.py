from rest_framework import serializers
from django.utils import timezone
from django.utils.translation import gettext as _
from calories_tracker import models
from calories_tracker.reusing.request_casting import object_from_url


class ActivitiesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.Activities
        fields = ('url', 'id', 'name', 'description', 'multiplier', 'localname')

    def get_localname(self, obj):
        return  _(obj.name)

class AdditiveRisksSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.AdditiveRisks
        fields = ('url', 'id', 'name', 'localname')

    def get_localname(self, obj):
        return  _(obj.name)

class AdditivesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Additives
        fields = ('url', 'id', 'name', 'description', 'additive_risks')
        
class BiometricsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Biometrics
        fields = ('url', 'id', 'datetime', 'height', 'weight', 'weight_wishes', 'activities')
                
    def create(self, validated_data):
        validated_data['user']=self.context.get("request").user
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        return created

class CompaniesSerializer(serializers.HyperlinkedModelSerializer):
    is_deletable = serializers.SerializerMethodField()
    is_editable = serializers.SerializerMethodField()

    class Meta:
        model = models.Companies
        fields = ('url', 'id', 'name', 'last', 'obsolete', 'system_companies', 'is_editable', 'is_deletable')
        
    def create(self, validated_data):
        validated_data['user']=self.context.get("request").user
        validated_data['last']=timezone.now()
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        return created

    def get_is_deletable(self, o):
        return o.is_deletable()

    def get_is_editable(self, o):
        return o.is_editable()

class ElaboratedProductsProductsInThroughSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ElaboratedProductsProductsInThrough

        fields = ('products',  'amount', 'elaborated_products' )
        
class ElaboratedProductsSerializer(serializers.HyperlinkedModelSerializer):
    is_deletable = serializers.SerializerMethodField()
    uses = serializers.SerializerMethodField()
    products_in = ElaboratedProductsProductsInThroughSerializer(many=True, read_only=True, source="elaboratedproductsproductsinthrough_set")
    class Meta:
        model = models.ElaboratedProducts
        fields = ('url', 'id', 'name', 'last', 'obsolete', 'food_types', 'final_amount', 'products_in', 'uses', 'is_deletable')

    def create(self, validated_data):
        data=self.context.get("request").data
        validated_data['user']=self.context.get("request").user
        validated_data['last']=timezone.now()
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        created.save()
        for d in data["products_in"]:
            print(d)
            #Create all new
            th=models.ElaboratedProductsProductsInThrough()
            th.amount=d["amount"]
            th.products=object_from_url(d["products"], models.Products)
            th.elaborated_products=created
            th.save()
        created.update_associated_product()
        return created
        
         
    def update(self, instance, validated_data):
        data=self.context.get("request").data
        validated_data['user']=self.context.get("request").user
        validated_data['last']=timezone.now()
        
        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
        updated.save()
        
        #Delete all
        qs=models.ElaboratedProductsProductsInThrough.objects.filter(elaborated_products=updated)
        if len(qs)>0:
            qs.delete()

        #Create all new
        for d in data["products_in"]:
            th=models.ElaboratedProductsProductsInThrough()
            th.amount=d["amount"]
            th.products=object_from_url(d["products"], models.Products)
            th.elaborated_products=updated
            th.save()
        
        updated.update_associated_product()
        return updated
        
        
    def get_is_deletable(self, o):
        return o.is_deletable()
        
    def get_uses(self, o):
        return o.uses()
class FoodTypesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.FoodTypes
        fields = ('url', 'id', 'name', 'localname')
    def get_localname(self, obj):
        return  _(obj.name)

class FormatsSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.Formats
        fields = ('url', 'id', 'name', 'localname')

    def get_localname(self, obj):
        return  _(obj.name)

class MealsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Meals
        fields = ('url', 'id', 'datetime', 'products', 'amount')       

    def create(self, validated_data):
        validated_data['user']=self.context.get("request").user
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        return created

class ProductsFormatsThroughSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ProductsFormatsThrough

        fields = ('amount', 'formats')
        
class ProductsSerializer(serializers.HyperlinkedModelSerializer):
    formats= ProductsFormatsThroughSerializer(many=True, read_only=True, source="productsformatsthrough_set")
    is_deletable = serializers.SerializerMethodField()
    is_editable = serializers.SerializerMethodField()
    uses = serializers.SerializerMethodField()


    class Meta:
        model = models.Products
        fields = ('url', 'id', 'additives', 'amount', 'calcium', 'calories','carbohydrate', 'cholesterol', 'companies', 'elaborated_products', 'fat', 'ferrum', 'fiber', 'food_types', 'formats', 'glutenfree', 'magnesium', 'name', 'obsolete', 'phosphor', 'potassium', 'protein', 'salt', 'saturated_fat', 'sodium', 'sugars', 'system_products', 'version', 'version_description', 'version_parent', 'is_editable', 'is_deletable', 'uses')
        
    def create(self, validated_data):
        data=self.context.get("request").data
        validated_data['user']=self.context.get("request").user
        validated_data['version']=timezone.now()
        created=serializers.HyperlinkedModelSerializer.create(self,  validated_data)
        created.save()
        for d in data["formats"]:
            #Create all new
            th=models.ProductsFormatsThrough()
            th.amount=d["amount"]
            th.formats=object_from_url(d["formats"], models.Formats)
            th.products=created
            th.save()
        
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
        for d in data["formats"]:
            th=models.ProductsFormatsThrough()
            th.amount=d["amount"]
            th.formats=object_from_url(d["formats"], models.Formats)
            th.products=updated
            th.save()
        
        return updated

    def get_is_deletable(self, o):
        return o.is_deletable()

    def get_is_editable(self, o):
        return o.is_editable()
        
    def get_uses(self, o):
        return o.uses()

class ProfilesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Profiles
        fields = ('url', 'id', 'birthday', 'male')

class SystemCompaniesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SystemCompanies
        fields = ('url', 'id', 'name', 'last', 'obsolete')


class SystemProductsFormatsThroughSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SystemProductsFormatsThrough

        fields = ('id','system_products',  'amount', 'formats' )
        
class SystemProductsSerializer(serializers.HyperlinkedModelSerializer):
    formats= SystemProductsFormatsThroughSerializer(many=True, read_only=True, source="systemproductsformatsthrough_set")

    class Meta:
        model = models.SystemProducts
        fields = ('url', 'id', 'additives', 'amount', 'calcium', 'calories','carbohydrate', 'cholesterol', 'fat', 'ferrum', 'fiber', 'food_types', 'formats', 'glutenfree', 'magnesium', 'name', 'obsolete', 'phosphor', 'potassium', 'protein', 'salt', 'saturated_fat', 'sodium', 'sugars', 'system_companies', 'version', 'version_description', 'version_parent')



class WeightWishesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.WeightWishes
        fields = ('url', 'id', 'name', 'localname')

    def get_localname(self, obj):
        return  _(obj.name)
