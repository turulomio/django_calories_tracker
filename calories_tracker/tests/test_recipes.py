from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models


def test_recipes(self):
    tests_helpers.common_tests_Private(self,  '/api/recipes/', models.Recipes.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)

    #Merge recipes
    dict_recipe_main=tests_helpers.client_post(self, self.client_authorized_1,  "/api/recipes/", models.Recipes.post_payload(),  status.HTTP_201_CREATED)
    self.assertEqual(len(dict_recipe_main["elaborations"]), 0)
    self.assertEqual(len(dict_recipe_main["recipes_links"]), 0)
    dict_recipe_1=tests_helpers.client_post(self, self.client_authorized_1,  "/api/recipes/", models.Recipes.post_payload(),  status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1,  "/api/recipes_links/", models.RecipesLinks.post_payload(recipes=dict_recipe_1["url"]),  status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1,  "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipe_1["url"]),  status.HTTP_201_CREATED)
    dict_recipe_2=tests_helpers.client_post(self, self.client_authorized_1,  "/api/recipes/", models.Recipes.post_payload(),  status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1,  "/api/recipes_links/", models.RecipesLinks.post_payload(recipes=dict_recipe_2["url"]),  status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1,  "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipe_2["url"]),  status.HTTP_201_CREATED)

    # Merge with main recipe on list
    dict_merged=tests_helpers.client_post(self, self.client_authorized_1, dict_recipe_main["url"]+"merge/", {"recipes":[dict_recipe_1["url"], dict_recipe_2["url"], dict_recipe_main["url"]]},  status.HTTP_400_BAD_REQUEST)
    self.assertEqual(dict_merged, "You should not pass the recipe that will remain in the list of recipes to be merged") 
    # Merge without main recipe on list
    dict_merged=tests_helpers.client_post(self, self.client_authorized_1, dict_recipe_main["url"]+"merge/", {"recipes":[dict_recipe_1["url"], dict_recipe_2["url"]]},  status.HTTP_200_OK)
    ## Checks that have 2 elaborations and recipes_links
    self.assertEqual(len(dict_merged["elaborations"]), 2)
    self.assertEqual(len(dict_merged["recipes_links"]), 2)
    
    ## Checks that merged recipes are deleted
    tests_helpers.client_get(self, self.client_authorized_1, dict_recipe_1["url"], status.HTTP_404_NOT_FOUND)        
    tests_helpers.client_get(self, self.client_authorized_1, dict_recipe_2["url"], status.HTTP_404_NOT_FOUND)
