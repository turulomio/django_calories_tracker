from django.urls import path,  include
from django.contrib import admin# Need to import this since auth models get registered on import.

from rest_framework import routers

from calories_tracker import views as calories_tracker_views
router = routers.DefaultRouter()
router.register(r'weight_wishes', calories_tracker_views.WeightWishesViewSet)
router.register(r'activities', calories_tracker_views.ActivitiesViewSet)
router.register(r'additive_risks', calories_tracker_views.AdditiveRisksViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
    path('admin/', admin.site.urls),
]
