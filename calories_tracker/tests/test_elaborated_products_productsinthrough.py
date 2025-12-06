from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

def test_elaborated_products_productsinthrough(self):
    """
        Al ser un through no funcionan el common_tests_Private
    """
    dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
    dict_elaborated_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborated_products/", models.ElaboratedProducts.post_payload(), status.HTTP_201_CREATED)

    #Testing all actions
    tests_helpers.common_tests_Private(self, '/api/elaboratedproductsproductsinthrough/', models.ElaboratedProductsProductsInThrough.post_payload(products=dict_products["url"], elaborated_products=dict_elaborated_products["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)

