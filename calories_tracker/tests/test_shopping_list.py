from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

def test_shopping_list(self):
    dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
    dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
    dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
    
    # Elaboration without products_in
    shopping_list=tests_helpers.client_post(self, self.client_authorized_1, "/shopping_list/", {"elaborations": [dict_elaborations["url"], ]}, status.HTTP_200_OK)
    print(shopping_list)
    
    # Elaboration with products_in
    tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  status.HTTP_201_CREATED)
    shopping_list=tests_helpers.client_post(self, self.client_authorized_1, "/shopping_list/", {"elaborations": [dict_elaborations["url"], ]}, status.HTTP_200_OK)
    print(shopping_list)
    
    # Trying to get from client_authorized_2
    tests_helpers.client_post(self, self.client_authorized_2, "/shopping_list/", {"elaborations": [dict_elaborations["url"], ]}, status.HTTP_400_BAD_REQUEST)
