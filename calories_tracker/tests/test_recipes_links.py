from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

    
def test_recipes_links(self):             
    dict_recipe=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
    tests_helpers.common_tests_Private(self,  '/api/recipes_links/', models.RecipesLinks.post_payload(recipes=dict_recipe["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
    
    
    tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes_links/?recipes={dict_recipe['url']}", status.HTTP_200_OK)
    tests_helpers.client_get(self, self.client_authorized_1, "/api/recipes_links/?recipes=rrrr", status.HTTP_200_OK)
    
    dict_recipe=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
