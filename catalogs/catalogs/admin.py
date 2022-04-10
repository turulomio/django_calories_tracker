from django.utils.translation import gettext_lazy as _
from catalogs.models import Activities, AdditiveRisks, WeightWishes
#from django.contrib.auth.models import User, Group
#from django.urls import reverse_lazy
from django.contrib import admin# Need to import this since auth models get registered on import.


class ActivitiesAdmin(admin.ModelAdmin):
    model = Activities
    ordering = ['name']
    list_display = ['name', 'description', 'multiplier']
    search_fields = ['name']
    list_filter = ('name', )
class AdditiveRisksAdmin(admin.ModelAdmin):
    model = AdditiveRisks
    list_display = ['name']
    
class WeightWishesAdmin(admin.ModelAdmin):
    model = WeightWishes
    list_display = ['name']


admin.site.site_title = _('Django Calories Tracker')
admin.site.site_header = _('Django Calories Tracker')
admin.site.index_title = _('My Django Calories Tracker administration')

admin.site.register(Activities, ActivitiesAdmin)
admin.site.register(AdditiveRisks, AdditiveRisksAdmin)
admin.site.register(WeightWishes, WeightWishesAdmin)
    
#admin.site.site_url = reverse_lazy('home') 
#admin.site.logout_template=reverse_lazy('home')

#admin.site.unregister(User)
#admin.site.unregister(Group)
