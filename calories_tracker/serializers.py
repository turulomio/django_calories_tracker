
from rest_framework import serializers
from django.utils.translation import gettext as _
from calories_tracker.models import WeightWishes


class WeightWishesSerializer(serializers.HyperlinkedModelSerializer):
    localname = serializers.SerializerMethodField()
    class Meta:
        model = WeightWishes
        fields = ('url', 'id', 'name', 'localname')

    def get_localname(self, obj):
        return  _(obj.name)
