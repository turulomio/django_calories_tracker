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
class CompaniesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Companies
        fields = ('url', 'id', 'name', 'last', 'obsolete', 'system_companies')
class SystemCompaniesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Companies
        fields = ('url', 'id', 'name', 'last', 'obsolete')


class WeightWishesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.WeightWishes
        fields = ('url', 'id', 'name', 'localname')

    def get_localname(self, obj):
        return  _(obj.name)
