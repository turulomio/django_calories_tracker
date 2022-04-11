from django.utils.translation import gettext_lazy as _
from catalogs.models import Activities, AdditiveRisks, WeightWishes, FoodTypes, Additives, Formats, SystemCompanies, SystemProducts
#from django.contrib.auth.models import User, Group
#from django.urls import reverse_lazy
from django.contrib import admin# Need to import this since auth models get registered on import.


class ActivitiesAdmin(admin.ModelAdmin):
    model = Activities
    ordering = ['multiplier']
    list_display = ['id','name', 'description', 'multiplier']
    search_fields = ['name', 'description']

class AdditivesAdmin(admin.ModelAdmin):
    model = Additives
    list_display = ['name']
class AdditiveRisksAdmin(admin.ModelAdmin):
    model = AdditiveRisks
    list_display = ['id','name']
    ordering = ['id']
    search_fields = ['name']

class FoodTypesAdmin(admin.ModelAdmin):
    model = FoodTypes
    list_display = ['id','name']
    ordering = ['id']
    search_fields = ['name']

class FormatsAdmin(admin.ModelAdmin):
    model = Formats
    list_display = ['name']
    
class SystemCompaniesAdmin(admin.ModelAdmin):
    model = WeightWishes
    list_display = ['name']
class SystemProductsAdmin(admin.ModelAdmin):
    model = WeightWishes
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
admin.site.register(FoodTypes, FoodTypesAdmin)
    
admin.site.register(Additives, AdditivesAdmin)
    
admin.site.register(Formats, FormatsAdmin)
admin.site.register(SystemCompanies, SystemCompaniesAdmin)
admin.site.register(SystemProducts, SystemProductsAdmin)
    
#admin.site.site_url = reverse_lazy('home') 
#admin.site.logout_template=reverse_lazy('home')

#admin.site.unregister(User)
#admin.site.unregister(Group)
