from django.utils.translation import gettext_lazy as _
from calories_tracker.models import Activities, AdditiveRisks, ProductsFormatsThrough, ElaboratedProductsProductsInThrough, ProductsInElaboratedProducts, Biometrics, Products, Meals, WeightWishes, FoodTypes, Additives, Formats, SystemCompanies, SystemProducts, Companies, ElaboratedProducts
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
class ProductsAdminForm(ModelForm):
    class Meta:
        model = Products
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
    list_filter = ['additive_risks']
    
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


##### NOT CATALOG TABLES

    
class BiometricsAdmin(admin.ModelAdmin):
    model = Biometrics
    list_display = ['datetime','height', 'weight', 'weight_wishes', 'activities']
    ordering = ['datetime']

class CompaniesAdmin(admin.ModelAdmin):
    model = Companies
    list_display = ['name','system_companies', 'last', 'obsolete']
    ordering = ['name']
    search_fields = ['name', 'system_companies']
    
    
class ProductsInInline(admin.TabularInline):
    model = ElaboratedProductsProductsInThrough
    extra = 1
    
class ElaboratedProductsAdmin(admin.ModelAdmin):
    model = ElaboratedProducts
    list_display = ['name','food_types', 'final_amount','last', 'obsolete', 'user']
    ordering = ['name']
    search_fields = ['name']
    inlines = (ProductsInInline,)
    
    
class MealsAdmin(admin.ModelAdmin):
    model = Meals
    list_display = ['datetime','products', 'amount', 'user']
    ordering = ['datetime']
    search_fields = ['products', 'user']
    list_filter=['user']
    
    
    
class ProductsFormatsInLine(admin.TabularInline):
    model = ProductsFormatsThrough
    extra = 1
class ProductsAdmin(admin.ModelAdmin):
    model = Products
    form = ProductsAdminForm
    list_display = ['name','system_products', 'elaborated_products',  'version', 'obsolete']
    ordering = ['name']
    search_fields = ['name', 'system_products']
    list_filter=['user']
    inlines = (ProductsFormatsInLine,)

    
class ProductsInElaboratedProductsAdmin(admin.ModelAdmin):
    model = ProductsInElaboratedProducts
    list_display = ['products', 'amount',  'elaborated_products']
    ordering = ['elaborated_products']
    search_fields = ['elaborated_products']
    list_filter = ['elaborated_products', 'products']

    
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
##### NOT CATALOG TABLES
admin.site.register(Biometrics, BiometricsAdmin)
admin.site.register(Companies, CompaniesAdmin)
admin.site.register(ElaboratedProducts, ElaboratedProductsAdmin)
admin.site.register(Meals, MealsAdmin)
admin.site.register(Products, ProductsAdmin)
admin.site.register(ProductsInElaboratedProducts, ProductsInElaboratedProductsAdmin)
    
#admin.site.site_url = reverse_lazy('home') 
#admin.site.logout_template=reverse_lazy('home')

#admin.site.unregister(User)
#admin.site.unregister(Group)
