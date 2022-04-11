
from calories_tracker import serializers
from calories_tracker.models import WeightWishes
from decimal import Decimal
from rest_framework import viewsets, permissions


from django.core.serializers.json import DjangoJSONEncoder

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
        
        
class WeightWishesViewSet(viewsets.ModelViewSet):
    queryset = WeightWishes.objects.all()
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
