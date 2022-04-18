from django.urls import path,  include
from django.contrib import admin# Need to import this since auth models get registered on import.

from rest_framework import routers

from calories_tracker import views as calories_tracker_views
router = routers.DefaultRouter()
router.register(r'activities', calories_tracker_views.ActivitiesViewSet)
router.register(r'additive_risks', calories_tracker_views.AdditiveRisksViewSet)
router.register(r'additives', calories_tracker_views.AdditivesViewSet)
router.register(r'biometrics', calories_tracker_views.BiometricsViewSet)
router.register(r'companies', calories_tracker_views.CompaniesViewSet)
router.register(r'elaborated_products', calories_tracker_views.ElaboratedProductsViewSet)
router.register(r'food_types', calories_tracker_views.FoodTypesViewSet)
router.register(r'formats', calories_tracker_views.FormatsViewSet)
router.register(r'meals', calories_tracker_views.MealsViewSet)
router.register(r'products', calories_tracker_views.ProductsViewSet)
router.register(r'profiles', calories_tracker_views.ProfilesViewSet)
router.register(r'system_companies', calories_tracker_views.SystemCompaniesViewSet)
router.register(r'system_products', calories_tracker_views.SystemProductsViewSet)
router.register(r'weight_wishes', calories_tracker_views.WeightWishesViewSet)



urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    
    path('login/', calories_tracker_views.login, name="login"), 
    path('logout/', calories_tracker_views.logout, name="logout"), 
    path('time/', calories_tracker_views.Time, name='Time'),
    path('statistics/', calories_tracker_views.Statistics, name='Statistics'),
    path('system_products_to_products/', calories_tracker_views.SystemProduct2Product, name='SystemProduct2Product'),
]
