from rest_framework import serializers
from django.utils.translation import gettext as _
from calories_tracker import models


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
#    
#    ## Update doesn't update blob, only changes metadata
#    def update(self, instance, validated_data):
#        validated_data['blob']=instance.blob
#        updated=serializers.HyperlinkedModelSerializer.update(self, instance, validated_data)
#        return updated
class CompaniesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Companies
        fields = ('url', 'id', 'name', 'last', 'obsolete', 'system_companies')

class ElaboratedProductsProductsInThroughSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ElaboratedProductsProductsInThrough

        fields = ('id','products',  'amount', 'elaborated_products' )
        
class ElaboratedProductsSerializer(serializers.HyperlinkedModelSerializer):
    products_in = ElaboratedProductsProductsInThroughSerializer(many=True, read_only=True, source="elaboratedproductsproductsinthrough_set")
    class Meta:
        model = models.ElaboratedProducts
        fields = ('url', 'id', 'name', 'last', 'obsolete', 'food_types', 'final_amount', 'products_in')
        
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
        


class ProductsFormatsThroughSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.ProductsFormatsThrough

        fields = ('id','products',  'amount', 'formats' )
        
class ProductsSerializer(serializers.HyperlinkedModelSerializer):
    formats= ProductsFormatsThroughSerializer(many=True, read_only=True, source="productsformatsthrough_set")

    class Meta:
        model = models.Products
        fields = ('url', 'id', 'additives', 'amount', 'calcium', 'calories','carbohydrate', 'cholesterol', 'companies', 'elaborated_products', 'fat', 'ferrum', 'fiber', 'food_types', 'formats', 'glutenfree', 'magnesium', 'name', 'obsolete', 'phosphor', 'potassium', 'protein', 'salt', 'saturated_fat', 'sodium', 'sugars', 'system_products', 'version', 'version_description', 'version_parent')


class ProfilesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Profiles
        fields = ('url', 'id', 'birthday', 'male')

class SystemCompaniesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Companies
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
