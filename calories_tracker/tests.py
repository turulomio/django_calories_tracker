from calories_tracker import models
from calories_tracker import tests_helpers 
from calories_tracker.tests_helpers import  print_list, TestModelManager, hlu
from calories_tracker import tests_data as td
from django.contrib.auth.models import User
#from django.utils import timezone
from json import loads
from rest_framework.test import APIClient, APITestCase
print_list    

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

        client = APIClient()
        response = client.post('/login/', {'username': cls.user_testing.username, 'password': 'testing123',},format='json')
        result = loads(response.content)
        cls.token_user_testing = result
        
        response = client.post('/login/', {'username': cls.user_other.username, 'password': 'other123',},format='json')
        result = loads(response.content)
        cls.token_user_other = result
        
        cls.client_testing=APIClient()
        cls.client_testing.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_testing)

        cls.client_other=APIClient()
        cls.client_other.credentials(HTTP_AUTHORIZATION='Token ' + cls.token_user_other)

    def test_catalog_only_retrieve_and_list_actions_allowed(self):
        """
            Checks that catalog table can be only accesed to GET method to normal users
        """
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

        
