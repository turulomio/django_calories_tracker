from calories_tracker import views as calories_tracker_views
from calories_tracker import views_login as calories_tracker_views_login
from django.urls import path,  include
from django.contrib import admin# Need to import this since auth models get registered on import.
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'activities', calories_tracker_views.ActivitiesViewSet)
router.register(r'additive_risks', calories_tracker_views.AdditiveRisksViewSet)
router.register(r'additives', calories_tracker_views.AdditivesViewSet)
router.register(r'biometrics', calories_tracker_views.BiometricsViewSet)
router.register(r'companies', calories_tracker_views.CompaniesViewSet)
router.register(r'elaborated_products', calories_tracker_views.ElaboratedProductsViewSet)
router.register(r'elaborations', calories_tracker_views.ElaborationsViewSet)
router.register(r'elaborations_containers', calories_tracker_views.ElaborationsContainersViewSet)
router.register(r'elaborations_experiences', calories_tracker_views.ElaborationsExperiencesViewSet)
router.register(r'elaborations_texts', calories_tracker_views.ElaborationsTextsViewSet)
router.register(r'food_types', calories_tracker_views.FoodTypesViewSet)
router.register(r'files', calories_tracker_views.FilesViewSet)
router.register(r'formats', calories_tracker_views.FormatsViewSet)
router.register(r'meals', calories_tracker_views.MealsViewSet)
router.register(r'measures_types', calories_tracker_views.MeasuresTypesViewSet)
router.register(r'pill_events', calories_tracker_views.PillEventsViewSet)
router.register(r'pots', calories_tracker_views.PotsViewSet)
router.register(r'products', calories_tracker_views.ProductsViewSet)
router.register(r'recipes', calories_tracker_views.RecipesViewSet)
router.register(r'recipes_categories', calories_tracker_views.RecipesCategoriesViewSet)
router.register(r'recipes_links', calories_tracker_views.RecipesLinksViewSet)
router.register(r'recipes_links_types', calories_tracker_views.RecipesLinksTypesViewSet)
router.register(r'weight_wishes', calories_tracker_views.WeightWishesViewSet)
router.register(r'elaborationsproductsinthrough', calories_tracker_views.ElaborationsProductsInThroughViewSet)
router.register(r'elaboratedproductsproductsinthrough', calories_tracker_views.ElaboratedProductsProductsInThroughViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
    path('curiosities/', calories_tracker_views.Curiosities, name='Curiosities'),
    path('catalog_manager/', calories_tracker_views.CatalogManager, name='CatalogManager'),
    path('login/', calories_tracker_views_login.login, name="login"), 
    path('logout/', calories_tracker_views_login.logout, name="logout"), 
    path('time/', calories_tracker_views.Time, name='Time'),
    path('settings/', calories_tracker_views.Settings, name='Settings'),
    path('shopping_list/', calories_tracker_views.ShoppingList, name='ShoppingList'),
    path('statistics/', calories_tracker_views.Statistics, name='Statistics'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
