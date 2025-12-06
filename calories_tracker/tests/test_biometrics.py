from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models


class AdditivesRisksAPITest(CaloriesTrackerAPITestCase):
    def test_additive_risks(self):
        print(self.client_authorized_1)
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/additive_risks/', models.AdditiveRisks.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
        
                
class AdditivesAPITest(CaloriesTrackerAPITestCase):
    def test_additives(self):
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/additives/', models.Additives.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
        
class BiometricsAPITest(CaloriesTrackerAPITestCase):                
    def test_biometrics(self):
        tests_helpers.common_tests_Private(self,  '/api/biometrics/', models.Biometrics.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        #Today
        tests_helpers.client_get(self, self.client_authorized_1, f'/api/biometrics/?day={date.today()}', status.HTTP_200_OK)
        #Empty day
        tests_helpers.client_get(self, self.client_authorized_1, '/api/biometrics/?day=2022-01-01', status.HTTP_200_OK)

    def test_catalog_manager(self):
        r=tests_helpers.client_get(self, self.client_authorized_1, '/catalog_manager/', status.HTTP_200_OK)
        self.assertEqual(r, False)
        r=tests_helpers.client_get(self, self.client_catalog_manager, '/catalog_manager/', status.HTTP_200_OK)
        self.assertEqual(r, True)

    def test_companies(self):
        tests_helpers.common_tests_Private(self,  '/api/companies/', models.Companies.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)

    def test_curiosities(self):
        #Test empty database
        tests_helpers.client_get(self, self.client_authorized_1, "/curiosities/", status.HTTP_200_OK)
        #Adding some data to test curiosities again
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        tests_helpers.client_post(self, self.client_authorized_1,'/api/meals/', models.Meals.post_payload(products=dict_products["url"]), status.HTTP_201_CREATED)
        tests_helpers.client_post(self,  self.client_authorized_1, '/api/biometrics/', models.Biometrics.post_payload(),  status.HTTP_201_CREATED)
        tests_helpers.client_get(self, self.client_authorized_1, "/curiosities/", status.HTTP_200_OK)

        
        
    def test_elaborated_products(self):
        # Due to elaborated_products DELETE is not standard due to it doesn't return HTTP_204_NOT_CONTENT y RuntimeError
        # common_tests_PrivateCatalog code manually
        # START OF COPIED METHOD
        ### TEST OF CLIENT_AUTHENTICATED_1
        apitestclass=self
        client_authenticated_1=self.client_authorized_1
        client_authenticated_2=self.client_authorized_2
        client_anonymous=self.client_anonymous
        post_url="/api/elaborated_products/"
        post_payload=models.ElaboratedProducts.post_payload()
        ### ALWAYS ONE REGISTER TO TEST FALBACK ID
        dict_post=tests_helpers.client_post(apitestclass, client_authenticated_1, post_url, post_payload, status.HTTP_201_CREATED)
        
        ### TEST OF CLIENT_AUTHENTICATED_1
        tests_helpers.common_actions_tests(apitestclass, client_authenticated_1, post_url, post_payload, dict_post["id"], 
            post=status.HTTP_201_CREATED, 
            get=status.HTTP_200_OK, 
            list=status.HTTP_200_OK, 
            put=status.HTTP_200_OK, 
            patch=status.HTTP_200_OK, 
            delete=status.HTTP_200_OK
        )

        # 1 creates and 2 cant get
        r1=client_authenticated_1.post(post_url, post_payload, format="json")
        apitestclass.assertEqual(r1.status_code, status.HTTP_201_CREATED, f"{post_url}, {r1.content}")
        r1_id=loads(r1.content)["id"]

        hlu_id_r1=tests_helpers.hlu(post_url,r1_id)
        
        r=client_authenticated_2.get(hlu_id_r1)
        apitestclass.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND, f"{post_url}, {r.content}. Client2 can access Client1 post")

        ### TEST OF CLIENT_ANONYMOUS
        tests_helpers.common_actions_tests(apitestclass, client_anonymous, post_url, post_payload, dict_post["id"], 
            post=status.HTTP_401_UNAUTHORIZED, 
            get=status.HTTP_401_UNAUTHORIZED, 
            list=status.HTTP_401_UNAUTHORIZED, 
            put=status.HTTP_401_UNAUTHORIZED, 
            patch=status.HTTP_401_UNAUTHORIZED, 
            delete=status.HTTP_401_UNAUTHORIZED
        )     

        # END OF COPIED METHOD
        
                        
    def test_elaborations(self):
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/elaborations/', models.Elaborations.post_payload(dict_recipes["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        #Creates a new elaboration
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(dict_recipes["url"]), status.HTTP_201_CREATED)
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  status.HTTP_201_CREATED)
        tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborations_containers/', models.ElaborationsContainers.post_payload(elaborations=dict_elaborations["url"]),  status.HTTP_201_CREATED)
        
        tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "create_automatic_elaboration/", {"diners":8}, status.HTTP_200_OK)
        tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "create_automatic_elaboration/", {}, status.HTTP_400_BAD_REQUEST)
        tests_helpers.client_post(self, self.client_authorized_2, dict_elaborations["url"]+ "create_automatic_elaboration/", {"diners":10}, status.HTTP_404_NOT_FOUND)
        #Creates elaborated product
        tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "create_elaborated_product/", {"diners":8}, status.HTTP_200_OK)
        tests_helpers.client_post(self, self.client_authorized_2, dict_elaborations["url"]+ "create_elaborated_product/", {"diners":10}, status.HTTP_404_NOT_FOUND)        

    def test_elaborations_containers(self):  
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/elaborations_containers/', models.ElaborationsContainers.post_payload(elaborations=dict_elaborations["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
                                                                                        
    def test_elaborations_experiences(self):     
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/elaborations_experiences/', models.ElaborationsExperiences.post_payload(elaborations=dict_elaborations["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
    
    def test_elaborations_productsinthrough(self):
        """
            Al ser un through no funcionan el common_tests_Private
        """
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)

    def test_elaborated_products_productsinthrough(self):
        """
            Al ser un through no funcionan el common_tests_Private
        """
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        dict_elaborated_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborated_products/", models.ElaboratedProducts.post_payload(), status.HTTP_201_CREATED)

        #Testing all actions
        tests_helpers.common_tests_Private(self, '/api/elaboratedproductsproductsinthrough/', models.ElaboratedProductsProductsInThrough.post_payload(products=dict_products["url"], elaborated_products=dict_elaborated_products["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)


    def test_food_types(self):
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/food_types/', models.FoodTypes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
        
    def test_formats(self):
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/formats/', models.Formats.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
        
    def test_meals(self): 
        dict_products_1=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(name="Product 1"), status.HTTP_201_CREATED)
        dict_products_2=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(name="Product 2"), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/meals/', models.Meals.post_payload(products=dict_products_1["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        tests_helpers.client_post(self, self.client_authorized_1, "/api/meals/", models.Meals.post_payload(products=dict_products_2["url"], amount=1000), status.HTTP_201_CREATED)      

        #Ranking
        tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/ranking/',  status.HTTP_200_OK)
        tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/ranking/?from_date=2022-01-01',  status.HTTP_200_OK)
        tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/ranking/?from_date=202',  status.HTTP_200_OK)
        
        #Delete several
        lod_meals=tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/',  status.HTTP_200_OK)
        meals_to_delete=lod.lod2list(lod_meals, "url")
        self.assertEqual(len(meals_to_delete), 3 )
        tests_helpers.client_post(self, self.client_authorized_1,  '/api/meals/delete_several/',  meals_to_delete,  status.HTTP_400_BAD_REQUEST)
        tests_helpers.client_post(self, self.client_authorized_1,  '/api/meals/delete_several/',  {"meals":meals_to_delete },  status.HTTP_200_OK)

        lod_meals=tests_helpers.client_get(self, self.client_authorized_1,  '/api/meals/',  status.HTTP_200_OK)
        meals_to_delete=lod.lod2list(lod_meals, "url")
        self.assertEqual(len(meals_to_delete), 0 )
        
    def test_measures_types(self):
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/measures_types/', models.MeasuresTypes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                
    @tag("current")
    def test_pill_events(self):
        # Common vars
        pillname="Pill name"
        dt_from=timezone.now()
        days=5
        #LIST NOT STANDARD tests_helpers.common_tests_Private(self,  '/api/pill_events/', models.PillEvents.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        
        # Removes pillevents from dt. Round timezones use 1 second minus
        #deleted=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/delete_from_dt/',  {"pillname": "Pill name",  "dt_from": timezone.now()-timedelta(hours=1)},  status.HTTP_200_OK)        

        # POST
        tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/', models.PillEvents.post_payload(), status.HTTP_201_CREATED)

        # LIST
        tests_helpers.client_get(self, self.client_authorized_1, '/api/pill_events/', status.HTTP_400_BAD_REQUEST)
        lod_pe=tests_helpers.client_get(self, self.client_authorized_1, f'/api/pill_events/?year={dt_from.year}&month={dt_from.month}', status.HTTP_200_OK)
        self.assertEqual(len(lod_pe), 1)
        # DELETE
        tests_helpers.client_delete(self, self.client_authorized_1, lod_pe[0]["url"], {}, status.HTTP_204_NO_CONTENT)


        
        # Set pillevents each dt
        lod_pe=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/set_each_day/',  {"pillname": pillname,  "dt_from": dt_from, "days": days},  status.HTTP_200_OK)
        self.assertEqual(len(lod_pe), 5)

        deleted=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/delete_from_dt/',  {"pillname": pillname,  "dt_from": dt_from-timedelta(seconds=1)},  status.HTTP_200_OK)        
        self.assertEqual(deleted[0], 5)
        
        # Each n hours
        lod_pe=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/set_each_n_hours/',  {"pillname": pillname,  "dt_from": dt_from, "hours": 8,  "number":9},  status.HTTP_200_OK)
        self.assertEqual(len(lod_pe), 9)
        deleted=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/delete_from_dt/',  {"pillname": pillname,  "dt_from": dt_from-timedelta(seconds=1)},  status.HTTP_200_OK)        
        self.assertEqual(deleted[0], 9)
        
        
    def test_pots(self):
        tests_helpers.common_tests_Private(self,  '/api/pots/', models.Pots.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
    
    def test_products(self):
        tests_helpers.common_tests_Private(self,  '/api/products/', models.Products.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)


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


    def test_recipes_links(self):             
        dict_recipe=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/recipes_links/', models.RecipesLinks.post_payload(recipes=dict_recipe["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        
        
        tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes_links/?recipes={dict_recipe['url']}", status.HTTP_200_OK)
        tests_helpers.client_get(self, self.client_authorized_1, "/api/recipes_links/?recipes=rrrr", status.HTTP_200_OK)
        
        dict_recipe=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)

    def test_recipes_categories(self):
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/recipes_categories/', models.RecipesCategories.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                
    def test_recipes_links_types(self):
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/recipes_links_types/', models.RecipesLinksTypes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)

    def test_settings(self):
        #Get
        tests_helpers.client_get(self, self.client_authorized_1, "/settings/", status.HTTP_200_OK)
        #Bad post
        tests_helpers.client_post(self, self.client_authorized_1, "/settings/",  {}, status.HTTP_400_BAD_REQUEST)
        #Good post
        tests_helpers.client_post(self, self.client_authorized_1, "/settings/",  {'first_name': 'Testing', 'last_name': 'Testing', 'last_login': '2023-06-13T07:05:01.293Z', 'email': 'testing@testing.com', 'birthday': '2000-01-01', 'male': True}, status.HTTP_200_OK)
        #Get again
        tests_helpers.client_get(self, self.client_authorized_1, "/settings/", status.HTTP_200_OK)
        
        
        
    def test_shopping_list(self):
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
        
        # Elaboration without products_in
        shopping_list=tests_helpers.client_post(self, self.client_authorized_1, "/shopping_list/", {"elaborations": [dict_elaborations["url"], ]}, status.HTTP_200_OK)
        print(shopping_list)
        
        # Elaboration with products_in
        tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  status.HTTP_201_CREATED)
        shopping_list=tests_helpers.client_post(self, self.client_authorized_1, "/shopping_list/", {"elaborations": [dict_elaborations["url"], ]}, status.HTTP_200_OK)
        print(shopping_list)
        
        # Trying to get from client_authorized_2
        tests_helpers.client_post(self, self.client_authorized_2, "/shopping_list/", {"elaborations": [dict_elaborations["url"], ]}, status.HTTP_400_BAD_REQUEST)

    def test_statistics(self):
        tests_helpers.client_get(self, self.client_authorized_1, "/statistics/", status.HTTP_200_OK)

    def test_weight_wishes(self):
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/weight_wishes/', models.WeightWishes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)