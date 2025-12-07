from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

def test_meals(self): 
    dict_products_1=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(name="Product 1"), status.HTTP_201_CREATED)
    dict_products_2=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(name="Product 2"), status.HTTP_201_CREATED)
    tests_helpers.common_tests_Private(self,  '/api/meals/', models.Meals.post_payload(products=dict_products_1["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
    tests_helpers.client_post(self, self.client_authorized_1, "/api/meals/", models.Meals.post_payload(products=dict_products_2["url"], amount=1000), status.HTTP_201_CREATED)      

    #Ranking
    tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/ranking/',  status.HTTP_200_OK)
    tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/ranking/?from_date=2022-01-01',  status.HTTP_200_OK)
    tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/ranking/?from_date=202',  status.HTTP_200_OK)
    
    #Delete several
    lod_meals=tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/',  status.HTTP_200_OK)
    meals_to_delete=lod.lod2list(lod_meals, "url")
    self.assertEqual(len(meals_to_delete), 3 )
    tests_helpers.client_post(self, self.client_authorized_1,  '/api/meals/delete_several/',  meals_to_delete,  status.HTTP_400_BAD_REQUEST)
    tests_helpers.client_post(self, self.client_authorized_1,  '/api/meals/delete_several/',  {"meals":meals_to_delete },  status.HTTP_200_OK)

    lod_meals=tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/',  status.HTTP_200_OK)
    meals_to_delete=lod.lod2list(lod_meals, "url")
    self.assertEqual(len(meals_to_delete), 0 )
