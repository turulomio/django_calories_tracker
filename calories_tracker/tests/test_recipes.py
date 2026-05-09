from calories_tracker import models
from . import tests_helpers
from rest_framework import status

def test_recipes(self):
    tests_helpers.common_tests_Private(self,  '/api/recipes/', models.Recipes.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)

def test_recipes_merge(self):
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

    # Check recipe last update has changed after merge
    self.assertNotEqual(dict_recipe_main["last"], dict_merged["last"])
    
    ## Checks that merged recipes are deleted
    tests_helpers.client_get(self, self.client_authorized_1, dict_recipe_1["url"], status.HTTP_404_NOT_FOUND)        
    tests_helpers.client_get(self, self.client_authorized_1, dict_recipe_2["url"], status.HTTP_404_NOT_FOUND)

def test_recipes_search_by_ingredients(self):
    # Create products
    product1 = tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(name="Ingredient A"), status.HTTP_201_CREATED)
    product2 = tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(name="Ingredient B"), status.HTTP_201_CREATED)
    product3 = tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(name="Ingredient C"), status.HTTP_201_CREATED)

    # Create recipes
    recipe_all_ingredients = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(name="Recipe with A, B, C"), status.HTTP_201_CREATED)
    recipe_subset_ingredients = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(name="Recipe with A, B"), status.HTTP_201_CREATED)
    recipe_other_ingredients = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(name="Recipe with C only"), status.HTTP_201_CREATED)
    recipe_no_ingredients = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(name="Recipe with no ingredients"), status.HTTP_201_CREATED)

    # Create elaborations for recipes
    elaboration_all = tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=recipe_all_ingredients["url"]), status.HTTP_201_CREATED)
    elaboration_subset = tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=recipe_subset_ingredients["url"]), status.HTTP_201_CREATED)
    elaboration_other = tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=recipe_other_ingredients["url"]), status.HTTP_201_CREATED)
    elaboration_no_ing = tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=recipe_no_ingredients["url"]), status.HTTP_201_CREATED)

    # Add products to elaborations
    tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborationsproductsinthrough/", models.ElaborationsProductsInThrough.post_payload(elaborations=elaboration_all["url"], products=product1["url"]), status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborationsproductsinthrough/", models.ElaborationsProductsInThrough.post_payload(elaborations=elaboration_all["url"], products=product2["url"]), status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborationsproductsinthrough/", models.ElaborationsProductsInThrough.post_payload(elaborations=elaboration_all["url"], products=product3["url"]), status.HTTP_201_CREATED)

    tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborationsproductsinthrough/", models.ElaborationsProductsInThrough.post_payload(elaborations=elaboration_subset["url"], products=product1["url"]), status.HTTP_201_CREATED)
    tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborationsproductsinthrough/", models.ElaborationsProductsInThrough.post_payload(elaborations=elaboration_subset["url"], products=product2["url"]), status.HTTP_201_CREATED)

    tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborationsproductsinthrough/", models.ElaborationsProductsInThrough.post_payload(elaborations=elaboration_other["url"], products=product3["url"]), status.HTTP_201_CREATED)

    # Test case 1: Search for all three ingredients (A, B, C)
    payload = {"products": [product1["url"], product2["url"], product3["url"]]}
    response = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/search_by_ingredients/", payload, status.HTTP_200_OK)
    self.assertEqual(len(response), 1)
    self.assertEqual(response[0]["id"], recipe_all_ingredients["id"])

    # Test case 2: Search for two ingredients (A, B)
    payload = {"products": [product1["url"], product2["url"]]}
    response = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/search_by_ingredients/", payload, status.HTTP_200_OK)
    self.assertEqual(len(response), 2) # Should match recipe_all_ingredients and recipe_subset_ingredients
    response_ids = [r["id"] for r in response]
    self.assertIn(recipe_all_ingredients["id"], response_ids)
    self.assertIn(recipe_subset_ingredients["id"], response_ids)

    # Test case 3: Search for one ingredient (C)
    payload = {"products": [product3["url"]]}
    response = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/search_by_ingredients/", payload, status.HTTP_200_OK)
    self.assertEqual(len(response), 2) # Should match recipe_all_ingredients and recipe_other_ingredients
    response_ids = [r["id"] for r in response]
    self.assertIn(recipe_all_ingredients["id"], response_ids)
    self.assertIn(recipe_other_ingredients["id"], response_ids)

    # Test case 4: Search for an ingredient not in any recipe
    product_non_existent = tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(name="Non-existent Ingredient"), status.HTTP_201_CREATED)
    payload = {"products": [product_non_existent["url"]]}
    response = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/search_by_ingredients/", payload, status.HTTP_200_OK)
    self.assertEqual(len(response), 0)

    # Test case 5: Empty product list
    payload = {"products": []}
    response = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/search_by_ingredients/", payload, status.HTTP_400_BAD_REQUEST)

    # Test case 6: Missing products parameter
    payload = {}
    response = tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/search_by_ingredients/", payload, status.HTTP_400_BAD_REQUEST)

    # Test case 7: Unauthorized user
    payload = {"products": [product1["url"]]}
    response = tests_helpers.client_post(self, self.client_anonymous, "/api/recipes/search_by_ingredients/", payload, status.HTTP_401_UNAUTHORIZED)
