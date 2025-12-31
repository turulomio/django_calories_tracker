from calories_tracker import models
from . import tests_helpers
from rest_framework import status

def test_elaborations_texts(self):     
    dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
    dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
    
    # CRUD relation ship one to one
    print(dict_elaborations["url"]+"set_elaboration_text/")
    dict_elaborations_text=tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+"set_elaboration_text/", models.ElaborationsTexts.post_payload(elaborations=dict_elaborations["url"]), status.HTTP_201_CREATED)
    # dict_elaborations_text=tests_helpers.client_put(self, self.client_authorized_1, dict_elaborations_text["url"], models.ElaborationsTexts.post_payload(elaborations=dict_elaborations["url"], text="Updated text"), status.HTTP_200_OK)
    # tests_helpers.client_get(self, self.client_authorized_1, dict_elaborations_text["url"], status.HTTP_200_OK, status.HTTP_200_OK)
    # tests_helpers.client_delete(self, self.client_authorized_1, dict_elaborations_text["url"], status.HTTP_204_NO_CONTENT)

    # # Check recipe last update has changed after post
    # dict_recipes_before=tests_helpers.client_get(self, self.client_authorized_1, dict_recipes["url"], status.HTTP_200_OK)
    # tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations_texts/", models.ElaborationsTexts.post_payload(elaborations=dict_elaborations["url"]), status.HTTP_201_CREATED)
    # dict_recipes_after=tests_helpers.client_get(self, self.client_authorized_1, dict_recipes["url"], status.HTTP_200_OK)
    # self.assertNotEqual(dict_recipes_before["last"], dict_recipes_after["last"])   