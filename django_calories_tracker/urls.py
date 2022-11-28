from django.urls import path,  include
from django.contrib import admin# Need to import this since auth models get registered on import.

from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from calories_tracker import views as calories_tracker_views
from calories_tracker.reusing import views_login as calories_tracker_views_login

router = routers.DefaultRouter()
router.register(r'activities', calories_tracker_views.ActivitiesViewSet)
router.register(r'additive_risks', calories_tracker_views.AdditiveRisksViewSet)
router.register(r'additives', calories_tracker_views.AdditivesViewSet)
router.register(r'biometrics', calories_tracker_views.BiometricsViewSet)
router.register(r'companies', calories_tracker_views.CompaniesViewSet)
router.register(r'elaborated_products', calories_tracker_views.ElaboratedProductsViewSet)
router.register(r'elaborations', calories_tracker_views.ElaborationsViewSet)
router.register(r'elaborations_steps', calories_tracker_views.ElaborationsStepsViewSet)
router.register(r'food_types', calories_tracker_views.FoodTypesViewSet)
router.register(r'formats', calories_tracker_views.FormatsViewSet)
router.register(r'meals', calories_tracker_views.MealsViewSet)
router.register(r'pots', calories_tracker_views.PotsViewSet)
router.register(r'products', calories_tracker_views.ProductsViewSet)
router.register(r'recipes', calories_tracker_views.RecipesViewSet)
router.register(r'recipes_full', calories_tracker_views.RecipesFullViewSet, "recipes_full")
router.register(r'recipes_categories', calories_tracker_views.RecipesCategoriesViewSet)
router.register(r'recipes_links', calories_tracker_views.RecipesLinksViewSet)
router.register(r'recipes_links_types', calories_tracker_views.RecipesLinksTypesViewSet)
router.register(r'steps', calories_tracker_views.StepsViewSet)
router.register(r'stir_types', calories_tracker_views.StirTypesViewSet)
router.register(r'system_companies', calories_tracker_views.SystemCompaniesViewSet)
router.register(r'system_products', calories_tracker_views.SystemProductsViewSet)
router.register(r'weight_wishes', calories_tracker_views.WeightWishesViewSet)
router.register(r'temperatures_types', calories_tracker_views.TemperaturesTypesViewSet)
router.register(r'elaborationsproductsinthrough', calories_tracker_views.ElaborationsProductsInThrough)





urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('curiosities/', calories_tracker_views.Curiosities, name='Curiosities'),
    path('catalog_manager/', calories_tracker_views.CatalogManager, name='CatalogManager'),
    path('login/', calories_tracker_views_login.login, name="login"), 
    path('logout/', calories_tracker_views_login.logout, name="logout"), 
    path('maintenance/catalogs/update/', calories_tracker_views.MaintenanceCatalogsUpdate, name='MaintenanceCatalogsUpdate'),
    path('meals/ranking/', calories_tracker_views.MealsRanking, name='MealsRanking'),
    path('products/datatransfer/', calories_tracker_views.ProductsDataTransfer, name='ProductsDataTransfer'),
    path('time/', calories_tracker_views.Time, name='Time'),
    path('settings/', calories_tracker_views.Settings, name='Settings'),
    path('statistics/', calories_tracker_views.Statistics, name='Statistics'),
    path('products_to_system_products/', calories_tracker_views.Product2SystemProduct, name='Product2SystemProduct'),
    path('system_products_to_products/', calories_tracker_views.SystemProduct2Product, name='SystemProduct2Product'),
    path('system_companies_to_companies/', calories_tracker_views.SystemCompany2Company, name='SystemCompany2Company'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
