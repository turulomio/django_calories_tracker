from calories_tracker import models
from . import tests_helpers
from rest_framework import status


def test_elaborations_productsinthrough(self):
    """
        Al ser un through no funcionan el common_tests_Private
    """
    dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
    dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
    dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
    
    #Check all
    tests_helpers.common_tests_Private(self,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)

    # Check recipe last update has changed upter post
    dict_recipes_before=tests_helpers.client_get(self, self.client_authorized_1, dict_recipes["url"], status.HTTP_200_OK)
    tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborationsproductsinthrough/", models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]), status.HTTP_201_CREATED)
    dict_recipes_after=tests_helpers.client_get(self, self.client_authorized_1, dict_recipes["url"], status.HTTP_200_OK)
    self.assertNotEqual(dict_recipes_before["last"], dict_recipes_after["last"])   