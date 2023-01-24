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
        
        cls.tmm=TestModelManager.from_module_with_testmodels("calories_tracker.tests_data")
        
        # User to test api
        cls.user_testing = User(
            email='testing@testing.com',
            first_name='Testing',
            last_name='Testing',
            username='testing',
        )
        cls.user_testing.set_password('testing123')
        cls.user_testing.save()
        
        # User to confront security
        cls.user_other = User(
            email='other@other.com',
            first_name='Other',
            last_name='Other',
            username='other',
        )
        cls.user_other.set_password('other123')
        cls.user_other.save()
        
                
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
        response = client.post('/login/', {'username': cls.user_testing.username, 'password': 'testing123',},format='json')
        result = loads(response.content)
        cls.token_user_testing = result
        
        response = client.post('/login/', {'username': cls.user_other.username, 'password': 'other123',},format='json')
        result = loads(response.content)
        cls.token_user_other = result

        response = client.post('/login/', {'username': cls.user_catalog_manager.username, 'password': 'catalog_manager123',},format='json')
        result = loads(response.content)
        cls.token_user_catalog_manager=result
        
        cls.client_testing=APIClient()
        cls.client_testing.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_testing)

        cls.client_other=APIClient()
        cls.client_other.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_other)
        
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
            tests_helpers.test_only_retrieve_and_list_actions_allowed(self, self.client_testing, tm)
            
        
    def test_cross_user_models_security(self):
        """
            Checks that a user can't see other user registers
        """
        print()
        for tm  in self.tmm.private():
            print("test_cross_user_models_security", tm.__name__)
            tests_helpers.test_cross_user_data_with_post(self, self.client_testing, self.client_other, tm)

        #Files only has get method. Post are mode from recipes_links, pots ....
        # I do this test manually
        file=models.Files()
        file.mime="image/png"
        file.content=b"MY FILE CONTENT"
        file.size=len(file.content)
        file.user=self.user_testing
        file.save()
        tests_helpers.test_cross_user_data(self, self.client_testing, self.client_other, hlu("files", file.id))

        #Test recipes_full i don't need to create, 
        recipe=td.tmRecipes.create(0, self.client_testing)
        tests_helpers.test_cross_user_data(self, self.client_testing, self.client_other, hlu("recipes_full", recipe["id"]))
  
    def test_crud_non_catalog(self):
        """
            Checks crud operations to not catalog models
        """
        print()
        for tm  in self.tmm.private():
            print("test_crud_non_catalog", tm.__name__)
            tests_helpers.test_crud(self, self.client_testing, tm)
            

    def test_anonymous_crud(self):
        """
            Anonymous user trys to crud
        """
        print()
        for tm  in self.tmm.private():
            print("test_anonymous_crud", tm.__name__)
            tests_helpers.test_crud_unauthorized_anonymous(self, self.client_anonymous, self.client_testing,  tm)

    def test_extra_actions(self):
        """
            Test extra actions security
        """
        print()
        print("test_extra_actions")
        
        # Update steps
        elaboration=td.tmElaborations.create(0, self.client_testing)
        url=f"{elaboration['url']}update_steps/"
        steps=[]
        elaboration_step=td.tmElaborationsSteps.create(0, self.client_testing)
        steps.append(elaboration_step)
        del elaboration_step["url"]#preparando elaboration_step, sin url
        steps.append(elaboration_step)#Adds second step
        r=self.client_testing.post(url, dumps({"steps":steps}), content_type='application/json') #Normal user
        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")

        #Meals ranking
        url="/api/meals/ranking/?from_date=2023-01-01"
        for i in range(3):
            td.tmMeals.create(0, self.client_testing)
        r=self.client_testing.get(url)
        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")
        
        #Products to system products
        product=td.tmProducts.create(0, self.client_testing)
        url=f"{product['url']}convert_to_system/"
        r=self.client_testing.post(url) #Normal user
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN,  f"Error @action {url}")
        r=self.client_catalog_manager.post(url) #CatalogManager user
        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")
        
        #System product to product
        url=f"{td.tmSystemProducts.hlu(28)}create_product/"
        r=self.client_testing.post(url) #Normal user
        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")
        self.assertNotEqual(loads(r.content)["system_products"], None,  f"Error getting system_companies {url}")
        
        #System company to company
        url=f"{td.tmSystemCompanies.hlu(27)}create_company/"
        r=self.client_testing.post(url) #Normal user
        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")
        self.assertNotEqual(loads(r.content)["system_companies"], None,  f"Error getting system_companies {url}")
        
    def test_elaborated_product(self):
        pass

    @tag('current')
    def test_recipes(self):
        mf=factory_helpers.MyFactory(factory.RecipesFactory, "Private", "/api/recipes/")
        recipe=mf.factory.create(user=self.user_testing, recipes_categories=factory.RecipesCategoriesFactory.create_batch(2))
        print(factory_helpers.serialize(recipe))
#        self.client_testing.post(mf.url,  mf.post_payload(user=self.user_testing))
