from calories_tracker import models, tests_helpers
from datetime import date
from django.contrib.auth.models import User
from django.test import tag
from json import loads
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import Group


tag, models

class CtTestCase(APITestCase):
    fixtures=["all.json"] #Para cargar datos por defecto

    @classmethod
    def setUpClass(cls):
        """
            Only instantiated once
        """
        super().setUpClass()
        
        # User to test api
        cls.user_authorized_1 = User(
            email='testing@testing.com',
            first_name='Testing',
            last_name='Testing',
            username='authorized_1',
        )
        cls.user_authorized_1.set_password('testing123')
        cls.user_authorized_1.save()
        
        # User to confront security
        cls.user_authorized_2 = User(
            email='other@other.com',
            first_name='Other',
            last_name='Other',
            username='authorized_2',
        )
        cls.user_authorized_2.set_password('other123')
        cls.user_authorized_2.save()
        
                
        # User to test api
        cls.user_catalog_manager = User(
            email='catalog_manager@catalog_manager.com',
            first_name='Catalog',
            last_name='Manager',
            username='catalog_manager',
        )
        cls.user_catalog_manager.set_password('catalog_manager123')
        cls.user_catalog_manager.save()
        cls.user_catalog_manager.groups.add(Group.objects.get(name='CatalogManager'))

        client = APIClient()
        response = client.post('/login/', {'username': cls.user_authorized_1.username, 'password': 'testing123',},format='json')
        result = loads(response.content)
        cls.token_user_authorized_1 = result
        
        response = client.post('/login/', {'username': cls.user_authorized_2.username, 'password': 'other123',},format='json')
        result = loads(response.content)
        cls.token_user_authorized_2 = result

        response = client.post('/login/', {'username': cls.user_catalog_manager.username, 'password': 'catalog_manager123',},format='json')
        result = loads(response.content)
        cls.token_user_catalog_manager=result
        
        cls.client_authorized_1=APIClient()
        cls.client_authorized_1.user=cls.user_authorized_1
        cls.client_authorized_1.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_authorized_1)

        cls.client_authorized_2=APIClient()
        cls.client_authorized_2.user=cls.user_authorized_2
        cls.client_authorized_2.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_authorized_2)
        
        cls.client_anonymous=APIClient()
        cls.client_anonymous.user=None
        
        cls.client_catalog_manager=APIClient()
        cls.client_catalog_manager.user=cls.user_catalog_manager
        cls.client_catalog_manager.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_catalog_manager)


    def test_activities(self):
        print()
        print("test_activities")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/activities/', models.Activities.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
        
        
    def test_additive_risks(self):
        print()
        print("test_additive_risks")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/additive_risks/', models.AdditiveRisks.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
        
                
    def test_additives(self):
        print()
        print("test_additives")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/additives/', models.Additives.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                        
    def test_biometrics(self):
        print()
        print("test_biometrics")
        tests_helpers.common_tests_Private(self,  '/api/biometrics/', models.Biometrics.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        #Today
        tests_helpers.client_get(self, self.client_authorized_1, f'/api/biometrics/?day={date.today()}', status.HTTP_200_OK)
        #Empty day
        tests_helpers.client_get(self, self.client_authorized_1, '/api/biometrics/?day=2022-01-01', status.HTTP_200_OK)

    def test_companies(self):
        print()
        print("test_companies")
        tests_helpers.common_tests_Private(self,  '/api/companies/', models.Companies.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        tests_helpers.common_tests_Private(self,  '/api/companies/', models.Companies.post_payload(system_companies=True),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)

    def test_curiosities(self):
        print()
        print("test_curiosities")        
        #Test empty database
        tests_helpers.client_get(self, self.client_authorized_1, "/curiosities/", status.HTTP_200_OK)
        #Adding some data to test curiosities again
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        tests_helpers.client_post(self, self.client_authorized_1,'/api/meals/', models.Meals.post_payload(products=dict_products["url"]), status.HTTP_201_CREATED)
        tests_helpers.client_post(self,  self.client_authorized_1, '/api/biometrics/', models.Biometrics.post_payload(),  status.HTTP_201_CREATED)
        tests_helpers.client_get(self, self.client_authorized_1, "/curiosities/", status.HTTP_200_OK)

        
        
    def test_elaborated_products(self):
        print()
        print("test_elaborated_products")
        tests_helpers.common_tests_Private(self,  '/api/elaborated_products/', models.ElaboratedProducts.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
                        
    def test_elaborations(self):
        print()
        print("test_elaborations")        
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/elaborations/', models.Elaborations.post_payload(dict_recipes["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        #Creates a new elaboration
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(dict_recipes["url"]), status.HTTP_201_CREATED)
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  status.HTTP_201_CREATED)
        tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborations_containers/', models.ElaborationsContainers.post_payload(elaborations=dict_elaborations["url"]),  status.HTTP_201_CREATED)
        
#        tests_helpers.client_post(
#            self,  
#            self.client_authorized_1, 
#            dict_elaborations["url"]+ "update_steps/", 
#            models.ElaborationsSteps.post_payload(
#                elaborations=dict_elaborations["url"], 
#                arr_products_in_step=[
#                    dict_productsin["url"],
#                    dict_productsin["url"],
#                ], 
#                arr_container=[
#                    dict_containers["url"],
#                    dict_containers["url"],
#                ]
#            ),
#            status.HTTP_201_CREATED
#        )
        tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "create_automatic_elaboration/", {"diners":8}, status.HTTP_200_OK)
        tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "create_automatic_elaboration/", {}, status.HTTP_400_BAD_REQUEST)
        tests_helpers.client_post(self, self.client_authorized_2, dict_elaborations["url"]+ "create_automatic_elaboration/", {"diners":10}, status.HTTP_404_NOT_FOUND)
        #Creates elaborated product
        tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "create_elaborated_product/", {"diners":8}, status.HTTP_200_OK)
        tests_helpers.client_post(self, self.client_authorized_2, dict_elaborations["url"]+ "create_elaborated_product/", {"diners":10}, status.HTTP_404_NOT_FOUND)
        #Generates elaboration PDF
        tests_helpers.client_post(self, self.client_authorized_1, dict_elaborations["url"]+ "generate_pdf/", {}, status.HTTP_200_OK)
        tests_helpers.client_post(self, self.client_authorized_2, dict_elaborations["url"]+ "generate_pdf/", {}, status.HTTP_404_NOT_FOUND)

        
        

    def test_elaborations_containers(self):
        print()
        print("test_elaborations_containers")        
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/elaborations_containers/', models.ElaborationsContainers.post_payload(elaborations=dict_elaborations["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
                                                                                        
    def test_elaborations_experiences(self):
        print()
        print("test_elaborations_experiences")        
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/elaborations_experiences/', models.ElaborationsExperiences.post_payload(elaborations=dict_elaborations["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
    
    def test_elaborations_productsinthrough(self):
        """
            Al ser un through no funcionan el common_tests_Private
        """
        print()
        print("test_elaborations_productsinthrough")
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
    @tag("current")
    def test_elaborations_steps(self):
        """
            Al ser un through no funcionan el common_tests_Private
        """
        print()
        print("test_elaborations_steps")
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
        lod_elaborations_productsin=[]
        lod_elaborations_productsin.append(tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  status.HTTP_201_CREATED))
        lod_elaborations_containers=[]
        lod_elaborations_containers.append(tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborations_containers/', models.ElaborationsContainers.post_payload(elaborations=dict_elaborations["url"]),  status.HTTP_201_CREATED))

        tests_helpers.client_post(
            self,  
            self.client_authorized_1, 
            dict_elaborations["url"]+ "update_steps/", 
            models.ElaborationsSteps.post_payload(
                elaborations=dict_elaborations["url"], 
                arr_products_in_step=[
                    [lod_elaborations_productsin[0]["url"],],  
                    [lod_elaborations_productsin[0]["url"],],  
                ], 
                arr_container=[
                    lod_elaborations_containers[0]["url"],
                    lod_elaborations_containers[0]["url"],
                ]
            ),  
            status.HTTP_200_OK
        )        

    def test_elaborated_products_productsinthrough(self):
        """
            Al ser un through no funcionan el common_tests_Private
        """
        print()
        print("test_elaborated_products_productsinthrough")
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        dict_elaborated_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborated_products/", models.ElaboratedProducts.post_payload(), status.HTTP_201_CREATED)

        #Testing all actions
        tests_helpers.common_tests_Private(self, '/api/elaboratedproductsproductsinthrough/', models.ElaboratedProductsProductsInThrough.post_payload(products=dict_products["url"], elaborated_products=dict_elaborated_products["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)


    def test_food_types(self):
        print()
        print("test_food_types")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/food_types/', models.FoodTypes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
        
    def test_formats(self):
        print() 
        print("test_formats")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/formats/', models.Formats.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
        
    def test_meals(self):
        print()
        print("test_meals")        
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/meals/', models.Meals.post_payload(products=dict_products["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)

    def test_measures_types(self):
        print()
        print("test_measures_types")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/measures_types/', models.MeasuresTypes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                
    def test_pots(self):
        print()
        print("test_pots")        
        tests_helpers.common_tests_Private(self,  '/api/pots/', models.Pots.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
                                      
    def test_products(self):
        print()
        print("test_products")        
        tests_helpers.common_tests_Private(self,  '/api/products/', models.Products.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        #Products to system products, SOLO DEBERIA PODER HACERLO UN USUARIO CON PERMISOS DE CATALOGO
#        dict_p=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
#        url=f"{dict_p['url']}convert_to_system/"        
#        tests_helpers.client_post(self, self.client_authorized_1, url, {}, status.HTTP_403_FORBIDDEN)
#        tests_helpers.client_post(self, self.client_catalog_manager, url, {}, status.HTTP_201_CREATED)

    def test_system_companies(self):
        """
            Checks system product logic
        """
        print()
        print("test_system_companies")


        tests_helpers.common_tests_PrivateEditableCatalog(self,  "/api/system_companies/", models.SystemCompanies.post_payload(), self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                
        #Creates a new system product
        dict_sp=tests_helpers.client_post(self, self.client_catalog_manager, "/api/system_companies/", models.SystemCompanies.post_payload(), status.HTTP_201_CREATED)

        #Client_autenticated_1 creates a company
        tests_helpers.client_post(self, self.client_authorized_1, dict_sp["url"]+"create_company/", {},  status.HTTP_200_OK)

        #Client_autenticated_2 creates a company
        tests_helpers.client_post(self, self.client_authorized_2, dict_sp["url"]+"create_company/", {} , status.HTTP_200_OK)
        
        #List of client_authorized_1 products len must be 1
        dict_all_p1=tests_helpers.client_get(self, self.client_authorized_1, "/api/companies/", status.HTTP_200_OK)
        self.assertEqual(len(dict_all_p1), 1)
        
        #List of client_authorized_2 products len must be 1
        dict_all_p2=tests_helpers.client_get(self, self.client_authorized_2, "/api/companies/", status.HTTP_200_OK)
        self.assertEqual(len(dict_all_p2), 1)
        
        #Search system companies
        dict_found=tests_helpers.client_get(self, self.client_authorized_1, "/api/system_companies/?search=Hacendado", status.HTTP_200_OK)
        self.assertEqual(len(dict_found),1 )
        
    def test_system_product(self):
        """
            Checks system product logic
        """
        print()
        print("test_system_product")


        tests_helpers.common_tests_PrivateEditableCatalog(self,  "/api/system_products/", models.SystemProducts.post_payload(), self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                
        #Creates a new system product
        dict_sp=tests_helpers.client_post(self, self.client_catalog_manager, "/api/system_products/", models.SystemProducts.post_payload(), status.HTTP_201_CREATED)

        #Client_autenticated_1 creates a product
        tests_helpers.client_post(self, self.client_authorized_1, dict_sp["url"]+"create_product/", {},  status.HTTP_200_OK)

        #Client_autenticated_2 creates a product
        tests_helpers.client_post(self, self.client_authorized_2, dict_sp["url"]+"create_product/", {} , status.HTTP_200_OK)
        
        #List of client_authorized_1 products len must be 1
        dict_all_p1=tests_helpers.client_get(self, self.client_authorized_1, "/api/products/", status.HTTP_200_OK)
        self.assertEqual(len(dict_all_p1), 1)
        
        #List of client_authorized_2 products len must be 1
        dict_all_p2=tests_helpers.client_get(self, self.client_authorized_2, "/api/products/", status.HTTP_200_OK)
        self.assertEqual(len(dict_all_p2), 1)
        
        #Search system product
        dict_found=tests_helpers.client_get(self, self.client_authorized_1, "/api/system_products/?search=Zucchini", status.HTTP_200_OK)
        self.assertEqual(len(dict_found),1 )

                                         
    def test_recipes(self):
        print()
        print("test_recipes")        
        tests_helpers.common_tests_Private(self,  '/api/recipes/', models.Recipes.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
                                         
    def test_recipes_links(self):
        print()
        print("test_recipes_links")                
        dict_recipe=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        tests_helpers.common_tests_Private(self,  '/api/recipes_links/', models.RecipesLinks.post_payload(recipes=dict_recipe["url"]),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
        
        
        tests_helpers.client_get(self, self.client_authorized_1, f"/api/recipes_links/?recipes={dict_recipe['url']}", status.HTTP_200_OK)
        tests_helpers.client_get(self, self.client_authorized_1, "/api/recipes_links/?recipes=rrrr", status.HTTP_200_OK)
        
        dict_recipe=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)





    def test_recipes_categories(self):
        print()
        print("test_recipes_categories")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/recipes_categories/', models.RecipesCategories.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                
    def test_recipes_links_types(self):
        print()
        print("test_recipes_links_types")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/recipes_links_types/', models.RecipesLinksTypes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)

    def test_settings(self):
        print()
        print("test_settings")
        #Get
        tests_helpers.client_get(self, self.client_authorized_1, "/settings/", status.HTTP_200_OK)
        #Bad post
        tests_helpers.client_post(self, self.client_authorized_1, "/settings/",  {}, status.HTTP_400_BAD_REQUEST)
        #Good post
        tests_helpers.client_post(self, self.client_authorized_1, "/settings/",  {'first_name': 'Testing', 'last_name': 'Testing', 'last_login': '2023-06-13T07:05:01.293Z', 'email': 'testing@testing.com', 'birthday': '2000-01-01', 'male': True}, status.HTTP_200_OK)
        #Get again
        tests_helpers.client_get(self, self.client_authorized_1, "/settings/", status.HTTP_200_OK)
        
        
        
    def test_shopping_list(self):
        print()
        print("test_shopping_list")
        dict_recipes=tests_helpers.client_post(self, self.client_authorized_1, "/api/recipes/", models.Recipes.post_payload(), status.HTTP_201_CREATED)
        dict_products=tests_helpers.client_post(self, self.client_authorized_1, "/api/products/", models.Products.post_payload(), status.HTTP_201_CREATED)
        dict_elaborations=tests_helpers.client_post(self, self.client_authorized_1, "/api/elaborations/", models.Elaborations.post_payload(recipes=dict_recipes["url"]), status.HTTP_201_CREATED)
        
        # Elaboration without products_in
        tests_helpers.client_post(self, self.client_authorized_1, "/shopping_list/", {"elaborations": [dict_elaborations["url"], ]}, status.HTTP_200_OK)
        tests_helpers.client_post(self, self.client_authorized_1,  '/api/elaborationsproductsinthrough/', models.ElaborationsProductsInThrough.post_payload(elaborations=dict_elaborations["url"], products=dict_products["url"]),  status.HTTP_201_CREATED)

        # Trying to get from client_authorized_2
        tests_helpers.client_post(self, self.client_authorized_2, "/shopping_list/", {"elaborations": [dict_elaborations["url"], ]}, status.HTTP_400_BAD_REQUEST)



    def test_statistics(self):
        print()
        print("test_statistics")
        tests_helpers.client_get(self, self.client_authorized_1, "/statistics/", status.HTTP_200_OK)

    def test_steps(self):
        print()
        print("test_steps")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/steps/', models.Steps.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)


    def test_stir_types(self):
        print()
        print("test_stir_types")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/stir_types/', models.StirTypes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                                                
    def test_temperatures_types(self):
        print()
        print("test_temperatures_types")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/temperatures_types/', models.TemperaturesTypes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                                                                
    def test_weight_wishes(self):
        print()
        print("test_weight_wishes")
        tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/weight_wishes/', models.WeightWishes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
                
