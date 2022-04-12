from django.utils.translation import gettext_lazy as _
from catalogs.models import Activities, SystemProductsFormatsThrough, AdditiveRisks, WeightWishes, FoodTypes, Additives, Formats, SystemCompanies, SystemProducts
#from django.contrib.auth.models import User, Group
#from django.urls import reverse_lazy
from django.contrib import admin# Need to import this since auth models get registered on import.
from django.forms import ModelForm


class SystemProductsAdminForm(ModelForm):
    class Meta:
        model = SystemProducts
        fields = '__all__' # required in new versions

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['additives'].queryset = (
            self.fields['additives'].queryset.order_by('name')
        )


class ProductAdmin(admin.ModelAdmin):
   list_display = ('name','platform')

class ActivitiesAdmin(admin.ModelAdmin):
    model = Activities
    ordering = ['multiplier']
    list_display = ['id','name', 'description', 'multiplier']
    search_fields = ['name', 'description']

class AdditivesAdmin(admin.ModelAdmin):
    model = Additives
    list_display = ['name', 'description', 'additive_risks']
    search_fields = ['name', 'description']
    list_filter = ['additive_risks']
    
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
    list_display = ['id','name']
    ordering = ['name']
    search_fields = ['name']
    
class SystemCompaniesAdmin(admin.ModelAdmin):
    model = SystemCompanies
    
    list_display = ['id','name', 'last', 'obsolete']
    ordering = ['name']
    search_fields = ['name']
    
    

    
class SystemProductsFormatsInLine(admin.TabularInline):
    model = SystemProductsFormatsThrough
    extra = 1
    
class SystemProductsAdmin(admin.ModelAdmin):
    model = SystemProducts
    list_display = ['id','name', 'system_companies', 'food_types',   'version', 'version_parent']
    ordering = ['name']
    search_fields = ['name']
    form = SystemProductsAdminForm
    inlines = (SystemProductsFormatsInLine,)

class WeightWishesAdmin(admin.ModelAdmin):
    model = WeightWishes
    list_display = ['id','name']
    ordering = ['name']
    search_fields = ['name']





admin.site.site_title = _('Django Calories Tracker. Catalog manager with dolt')
admin.site.site_header = _('Django Calories Tracker. Catalog manager with dolt')
admin.site.index_title = _('My Django Calories Tracker administration. Catalog manager with dolt')

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
