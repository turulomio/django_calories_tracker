from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models
def test_curiosities(self):
    #Test empty database
    tests_helpers.client_get(self, self.client_authorized_1, "/curiosities/", status.HTTP_200_OK)
    #Adding some data to test curiosities again
    dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1,'/api/meals/', models.Meals.post_payload(products=dict_products["url"]), status.HTTP_201_CREATED)
    tests_helpers.client_post(self,  self.client_authorized_1, '/api/biometrics/', models.Biometrics.post_payload(),  status.HTTP_201_CREATED)
    tests_helpers.client_get(self, self.client_authorized_1, "/curiosities/", status.HTTP_200_OK)
