from calories_tracker import models, commons
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
    search_ids_abc = commons.list_of_integers2string([product1["id"], product2["id"], product3["id"]], ",")
    response = tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes/?search=:INGREDIENTSALL {search_ids_abc}", status.HTTP_200_OK)
    self.assertEqual(len(response["results"]), 1)
    self.assertEqual(response["results"][0]["id"], recipe_all_ingredients["id"])

    # Test case 2: Search for two ingredients (A, B)
    search_ids_ab = commons.list_of_integers2string([product1["id"], product2["id"]], ",")
    response = tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes/?search=:INGREDIENTSALL {search_ids_ab}", status.HTTP_200_OK)
    self.assertEqual(len(response["results"]), 2) # Should match recipe_all_ingredients and recipe_subset_ingredients
    response_ids = [r["id"] for r in response["results"]]
    self.assertIn(recipe_all_ingredients["id"], response_ids)
    self.assertIn(recipe_subset_ingredients["id"], response_ids)

    # Test case 3: Search for one ingredient (C)
    search_ids_c = commons.list_of_integers2string([product3["id"]], ",")
    response = tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes/?search=:INGREDIENTSALL {search_ids_c}", status.HTTP_200_OK)
    self.assertEqual(len(response["results"]), 2) # Should match recipe_all_ingredients and recipe_other_ingredients
    response_ids = [r["id"] for r in response["results"]]
    self.assertIn(recipe_all_ingredients["id"], response_ids)
    self.assertIn(recipe_other_ingredients["id"], response_ids)

    # Test case 4: Search for an ingredient not in any recipe
    product_non_existent = tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(name="Non-existent Ingredient"), status.HTTP_201_CREATED)
    search_ids_non_existent = commons.list_of_integers2string([product_non_existent["id"]], ",")
    response = tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes/?search=:INGREDIENTSALL {search_ids_non_existent}", status.HTTP_200_OK)
    self.assertEqual(len(response["results"]), 0)

    # Test case 5: Empty product list
    # This tests the "Product IDs list cannot be empty" validation in views.py
    response = tests_helpers.client_get(self, self.client_authorized_1, "/api/recipes/?search=:INGREDIENTSALL ", status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response, "Product IDs list cannot be empty for :INGREDIENTSALL search")

    # Test case 6: Malformed product IDs (e.g., non-integer in list)
    # This tests the ValueError from commons.string2list_of_integers
    response = tests_helpers.client_get(self, self.client_authorized_1, "/api/recipes/?search=:INGREDIENTSALL 1,abc,3", status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response, "Error parsing ingredients: invalid product ID format")

    # Test case 7: Unauthorized user
    search_ids_product1 = commons.list_of_integers2string([product1["id"]], ",")
    response = tests_helpers.client_get(self, self.client_anonymous, f"/api/recipes/?search=:INGREDIENTSALL {search_ids_product1}", status.HTTP_401_UNAUTHORIZED)

    # Test case 8: Search for ingredients that are not all present in any recipe
    # For example, search for A, C. recipe_ab has A, recipe_c has C, recipe_abc has A,B,C.
    # Only recipe_abc should be returned.
    search_ids_ac = commons.list_of_integers2string([product1["id"], product3["id"]], ",")
    response = tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes/?search=:INGREDIENTSALL {search_ids_ac}", status.HTTP_200_OK)
    self.assertEqual(len(response["results"]), 1)
    self.assertEqual(response["results"][0]["id"], recipe_all_ingredients["id"])

    # --- Tests for :INGREDIENTSANY ---

    # Test case 9: Search for ingredients A, B (any of them)
    search_ids_ab_any = commons.list_of_integers2string([product1["id"], product2["id"]], ",")
    response = tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes/?search=:INGREDIENTSANY {search_ids_ab_any}", status.HTTP_200_OK)
    self.assertEqual(len(response["results"]), 2) # Should match recipe_all_ingredients and recipe_subset_ingredients
    response_ids = [r["id"] for r in response["results"]]
    self.assertIn(recipe_all_ingredients["id"], response_ids)
    self.assertIn(recipe_subset_ingredients["id"], response_ids)

    # Test case 10: Search for ingredient C (any)
    search_ids_c_any = commons.list_of_integers2string([product3["id"]], ",")
    response = tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes/?search=:INGREDIENTSANY {search_ids_c_any}", status.HTTP_200_OK)
    self.assertEqual(len(response["results"]), 2) # Should match recipe_all_ingredients and recipe_other_ingredients
    response_ids = [r["id"] for r in response["results"]]
    self.assertIn(recipe_all_ingredients["id"], response_ids)
    self.assertIn(recipe_other_ingredients["id"], response_ids)

    # Test case 11: Search for ingredient A (any)
    search_ids_a_any = commons.list_of_integers2string([product1["id"]], ",")
    response = tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes/?search=:INGREDIENTSANY {search_ids_a_any}", status.HTTP_200_OK)
    self.assertEqual(len(response["results"]), 2) # Should match recipe_all_ingredients and recipe_subset_ingredients
    response_ids = [r["id"] for r in response["results"]]
    self.assertIn(recipe_all_ingredients["id"], response_ids)
    self.assertIn(recipe_subset_ingredients["id"], response_ids)

    # Test case 12: Search for an ingredient not in any recipe (any)
    search_ids_non_existent_any = commons.list_of_integers2string([product_non_existent["id"]], ",")
    response = tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes/?search=:INGREDIENTSANY {search_ids_non_existent_any}", status.HTTP_200_OK)
    self.assertEqual(len(response["results"]), 0)

    # Test case 13: Empty product list for :INGREDIENTSANY
    response = tests_helpers.client_get(self, self.client_authorized_1, "/api/recipes/?search=:INGREDIENTSANY ", status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response, "Product IDs list cannot be empty for :INGREDIENTSANY search")

    # Test case 14: Malformed product IDs for :INGREDIENTSANY
    response = tests_helpers.client_get(self, self.client_authorized_1, "/api/recipes/?search=:INGREDIENTSANY 1,xyz,3", status.HTTP_400_BAD_REQUEST)
    self.assertEqual(response, "Error parsing ingredients: invalid product ID format")

    # Test case 15: Unauthorized user for :INGREDIENTSANY
    search_ids_product1_any = commons.list_of_integers2string([product1["id"]], ",")
    response = tests_helpers.client_get(self, self.client_anonymous, f"/api/recipes/?search=:INGREDIENTSANY {search_ids_product1_any}", status.HTTP_401_UNAUTHORIZED)
