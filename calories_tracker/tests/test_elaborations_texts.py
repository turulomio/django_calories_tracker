from calories_tracker import models
from . import tests_helpers
from rest_framework import status

def test_elaborations_texts(self):     
    dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
    dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
            
    # Initial creation/setting of elaboration text
    initial_text = "Initial elaboration text"
    dict_elaborations_with_text = tests_helpers.client_post(
        self, self.client_authorized_1, 
        dict_elaborations["url"] + "set_elaboration_text/", 
        {"text": initial_text}, # Correct payload format
        status.HTTP_200_OK # Should be 200 OK for an update/set action
    )
    # Verify the text was set. The response is the serialized Elaborations object.
    self.assertIn("elaborations_texts", dict_elaborations_with_text)
    self.assertEqual(dict_elaborations_with_text["elaborations_texts"]["text"], initial_text)

    # Update the elaboration text
    updated_text = "Updated elaboration text"
    dict_elaborations_updated_text = tests_helpers.client_post(
        self, self.client_authorized_1, 
        dict_elaborations["url"] + "set_elaboration_text/", 
        {"text": updated_text}, # Correct payload format
        status.HTTP_200_OK
    )
    # Verify the text was updated
    self.assertIn("elaborations_texts", dict_elaborations_updated_text)
    self.assertEqual(dict_elaborations_updated_text["elaborations_texts"]["text"], updated_text)

    # Check recipe last update has changed after post
    dict_recipes_before = tests_helpers.client_get(self, self.client_authorized_1, dict_recipes["url"], status.HTTP_200_OK)
    # Perform another update to trigger last_update change
    tests_helpers.client_post(
        self, self.client_authorized_1, 
        dict_elaborations["url"] + "set_elaboration_text/", 
        {"text": "Another update"}, 
        status.HTTP_200_OK
    )
    dict_recipes_after = tests_helpers.client_get(self, self.client_authorized_1, dict_recipes["url"], status.HTTP_200_OK)
    self.assertNotEqual(dict_recipes_before["last"], dict_recipes_after["last"])