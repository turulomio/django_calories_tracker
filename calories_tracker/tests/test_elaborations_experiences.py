from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

def test_elaborations_experiences(self):     
    dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
    dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
    tests_helpers.common_tests_Private(self,  '/api/elaborations_experiences/', models.ElaborationsExperiences.post_payload(elaborations=dict_elaborations["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)

