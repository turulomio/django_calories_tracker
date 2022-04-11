from django.utils.translation import gettext_lazy as _
from calories_tracker.models import Activities, AdditiveRisks, WeightWishes, FoodTypes, Additives, Formats, SystemCompanies, SystemProducts
#from django.contrib.auth.models import User, Group
#from django.urls import reverse_lazy
from django.contrib import admin# Need to import this since auth models get registered on import.
from django.forms import ModelForm

class ReadOnlyAdmin(admin.ModelAdmin):
    readonly_fields = []

    def get_readonly_fields(self, request, obj=None):
        return list(self.readonly_fields) + \
               [field.name for field in obj._meta.fields] + \
               [field.name for field in obj._meta.many_to_many]


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class SystemProductsAdminForm(ModelForm):
    class Meta:
        model = SystemProducts
        fields = '__all__' # required in new versions

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['additives'].queryset = (
            self.fields['additives'].queryset.order_by('name')
        )


class ActivitiesAdmin(ReadOnlyAdmin):
    model = Activities
    ordering = ['multiplier']
    list_display = ['id','name', 'description', 'multiplier']
    search_fields = ['name', 'description']

class AdditivesAdmin(ReadOnlyAdmin):
    model = Additives
    list_display = ['id','name', 'description', 'additive_risks']
    search_fields = ['name', 'description']
    list_filters = ['additive_risks']
    
class AdditiveRisksAdmin(ReadOnlyAdmin):
    model = AdditiveRisks
    list_display = ['id','name']
    ordering = ['id']
    search_fields = ['name']

class FoodTypesAdmin(ReadOnlyAdmin):
    model = FoodTypes
    list_display = ['id','name']
    ordering = ['id']
    search_fields = ['name']

class FormatsAdmin(ReadOnlyAdmin):
    model = Formats
    list_display = ['id','name']
    ordering = ['name']
    search_fields = ['name']
    
class SystemCompaniesAdmin(ReadOnlyAdmin):
    model = SystemCompanies
    
    list_display = ['id','name', 'last', 'obsolete']
    ordering = ['name']
    search_fields = ['name']

class SystemProductsAdmin(ReadOnlyAdmin):
    model = SystemProducts
    list_display = ['name']
    form = SystemProductsAdminForm
    
class WeightWishesAdmin(ReadOnlyAdmin):
    model = WeightWishes
    list_display = ['id','name']
    ordering = ['name']
    search_fields = ['name']





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
