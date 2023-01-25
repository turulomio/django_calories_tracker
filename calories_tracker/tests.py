from calories_tracker import models, factory
from calories_tracker import tests_helpers 
from calories_tracker.reusing import factory_helpers
from calories_tracker.tests_helpers import  print_list, TestModelManager, hlu
from calories_tracker import tests_data as td
from django.contrib.auth.models import User
from django.test import tag
#from django.utils import timezone
from json import loads, dumps
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import Group

print_list    
tag

class CtTestCase(APITestCase):
    fixtures=["all.json"] #Para cargar datos por defecto

    @classmethod
    def setUpClass(cls):
        """
            Only instantiated once
        """
        super().setUpClass()
        
        cls.factories_manager=factory_helpers.MyFactoriesManager()
        cls.factories_manager.append(factory.FoodTypesFactory, "PrivateEditableCatalog", "/api/food_types/")
        cls.factories_manager.append(factory.RecipesCategoriesFactory, "PrivateEditableCatalog", "/api/recipes_categories/")
        cls.factories_manager.append(factory.RecipesLinksTypesFactory, "PrivateEditableCatalog", "/api/recipes_links_types/")
        #cls.factories_manager.append(factory.RecipesFactory, "Private", "/api/recipes/")
#        cls.factories_manager.append(factory.RecipesLinksFactory, "Private", "/api/recipes_links/")

        cls.tmm=TestModelManager.from_module_with_testmodels("calories_tracker.tests_data")
        
        # User to test api
        cls.user_authorized_1 = User(
            email='testing@testing.com',
            first_name='Testing',
            last_name='Testing',
            username='testing',
        )
        cls.user_authorized_1.set_password('testing123')
        cls.user_authorized_1.save()
        
        # User to confront security
        cls.user_authorized_2 = User(
            email='other@other.com',
            first_name='Other',
            last_name='Other',
            username='other',
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
        cls.client_authorized_1.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_authorized_1)

        cls.client_authorized_2=APIClient()
        cls.client_authorized_2.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_authorized_2)
        
        cls.client_anonymous=APIClient()
        
        cls.client_catalog_manager=APIClient()
        cls.client_catalog_manager.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_catalog_manager)

    def test_catalog_only_retrieve_and_list_actions_allowed(self):
        """
            Checks that catalog table can be only accesed to GET method to normal users
        """
        print()
        for tm  in self.tmm.catalogs():
            print("test_catalog_only_retrieve_and_list_actions_allowed", tm.__name__)
            tests_helpers.test_only_retrieve_and_list_actions_allowed(self, self.client_authorized_1, tm)
            
        
    def test_cross_user_models_security(self):
        """
            Checks that a user can't see other user registers
        """
        print()
        for tm  in self.tmm.private():
            print("test_cross_user_models_security", tm.__name__)
            tests_helpers.test_cross_user_data_with_post(self, self.client_authorized_1, self.client_authorized_2, tm)

        #Files only has get method. Post are mode from recipes_links, pots ....
        # I do this test manually
        file=models.Files()
        file.mime="image/png"
        file.content=b"MY FILE CONTENT"
        file.size=len(file.content)
        file.user=self.user_authorized_1
        file.save()
        tests_helpers.test_cross_user_data(self, self.client_authorized_1, self.client_authorized_2, hlu("files", file.id))

        #Test recipes_full i don't need to create, 
        recipe=td.tmRecipes.create(0, self.client_authorized_1)
        tests_helpers.test_cross_user_data(self, self.client_authorized_1, self.client_authorized_2, hlu("recipes_full", recipe["id"]))
  
    def test_crud_non_catalog(self):
        """
            Checks crud operations to not catalog models
        """
        print()
        for tm  in self.tmm.private():
            print("test_crud_non_catalog", tm.__name__)
            tests_helpers.test_crud(self, self.client_authorized_1, tm)
            

    def test_anonymous_crud(self):
        """
            Anonymous user trys to crud
        """
        print()
        for tm  in self.tmm.private():
            print("test_anonymous_crud", tm.__name__)
            tests_helpers.test_crud_unauthorized_anonymous(self, self.client_anonymous, self.client_authorized_1,  tm)

    def test_extra_actions(self):
        """
            Test extra actions security
        """
        print()
        print("test_extra_actions")
        
        # Update steps
        elaboration=td.tmElaborations.create(0, self.client_authorized_1)
        url=f"{elaboration['url']}update_steps/"
        steps=[]
        elaboration_step=td.tmElaborationsSteps.create(0, self.client_authorized_1)
        steps.append(elaboration_step)
        del elaboration_step["url"]#preparando elaboration_step, sin url
        steps.append(elaboration_step)#Adds second step
        r=self.client_authorized_1.post(url, dumps({"steps":steps}), content_type='application/json') #Normal user
        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")

        #Meals ranking
        url="/api/meals/ranking/?from_date=2023-01-01"
        for i in range(3):
            td.tmMeals.create(0, self.client_authorized_1)
        r=self.client_authorized_1.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")
        
        #Products to system products
#        product=td.tmProducts.create(0, self.client_authorized_1)
#        url=f"{product['url']}convert_to_system/"
#        r=self.client_authorized_1.post(url) #Normal user
#        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN,  f"Error @action {url}")
#        r=self.client_catalog_manager.post(url) #CatalogManager user
#        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")
        
        #System product to product
        url=f"{td.tmSystemProducts.hlu(28)}create_product/"
        r=self.client_authorized_1.post(url) #Normal user
        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")
        self.assertNotEqual(loads(r.content)["system_products"], None,  f"Error getting system_companies {url}")
        
        #System company to company
        url=f"{td.tmSystemCompanies.hlu(27)}create_company/"
        r=self.client_authorized_1.post(url) #Normal user
        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")
        self.assertNotEqual(loads(r.content)["system_companies"], None,  f"Error getting system_companies {url}")
        

    def test_factory_by_type(self):
        print()
        for f in self.factories_manager:
            print("test_factory_by_type", f.type,  f)
            f.test_by_type(self, self.client_authorized_1, self.client_authorized_2, self.client_anonymous, self.client_catalog_manager)

    def test_elaborated_product(self):
        pass

    def test_recipes(self):
        mf=factory_helpers.MyFactory(factory.RecipesFactory, "Private", "/api/recipes/")
        recipe=mf.factory.create(user=self.user_authorized_1, recipes_categories=factory.RecipesCategoriesFactory.create_batch(2))
        recipe
#        print(factory_helpers.serialize(recipe))
#        self.client_authorized_1.post(mf.url,  mf.post_payload(user=self.user_authorized_1))

    def test_recipes_links(self):
        print()
        print("test_recipes_links")
        mf=factory_helpers.MyFactory(factory.RecipesLinksFactory, "Private", "/api/recipes_links/")
        payload=mf.post_payload(recipes__user=self.user_authorized_1)#Needs user to create a object, then delete id and url, and delete it. client.post doesn't need user
        print(payload)
        recipe=self.client_authorized_1.post(mf.url, payload)
        print(recipe, recipe.content)
