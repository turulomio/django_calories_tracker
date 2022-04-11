
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


class WeightWishesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = models.WeightWishes
        fields = ('url', 'id', 'name', 'localname')

    def get_localname(self, obj):
        return  _(obj.name)
