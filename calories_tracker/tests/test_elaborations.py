from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

    
def test_elaborations(self):
    dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
    tests_helpers.common_tests_Private(self,  '/api/elaborations/', models.Elaborations.post_payload(dict_recipes["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
    #Creates a new elaboration
    dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(dict_recipes["url"]), status.HTTP_201_CREATED)
    dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborations_containers/', models.ElaborationsContainers.post_payload(elaborations=dict_elaborations["url"]),  status.HTTP_201_CREATED)
    
    tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "create_automatic_elaboration/", {"diners":8}, status.HTTP_200_OK)
    tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "create_automatic_elaboration/", {}, status.HTTP_400_BAD_REQUEST)
    tests_helpers.client_post(self, self.client_authorized_2, dict_elaborations["url"]+ "create_automatic_elaboration/", {"diners":10}, status.HTTP_404_NOT_FOUND)
    #Creates elaborated product
    tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "create_elaborated_product/", {"diners":8}, status.HTTP_200_OK)
    tests_helpers.client_post(self, self.client_authorized_2, dict_elaborations["url"]+ "create_elaborated_product/", {"diners":10}, status.HTTP_404_NOT_FOUND)        
