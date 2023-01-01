#from calories_tracker import models
from calories_tracker import tests_helpers 
from calories_tracker.tests_helpers import  print_list, TestModelManager
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
            print("test_catalog_only_retrieve_and_list_actions_allowed", tm)
            tests_helpers.test_only_retrieve_and_list_actions_allowed(self, self.client_testing, tm)
            
        
    def test_cross_user_models_security(self):
        """
            Checks that a user can't see other user registers
        """
        for tm  in self.tmm.private():
            print("test_cross_user_models_security", tm)
            tests_helpers.test_cross_user_data_with_post(self, self.client_testing, self.client_other, tm)


#        tests_helpers.test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/elaborations_experiences/", {
#            "datetime": timezone.now(), 
#            "experience": "My elaboration experience", 
#            "elaborations": hlu("elaborations", elaboration["id"]),
#        })
#        
#        tests_helpers.test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/elaborations_steps/", {
#            "duration": "00:01:00", 
#            "order": 1, 
#            "elaborations": hlu("elaborations", elaboration["id"]),
#            "steps": hlu("steps", 2),
#        })
#        
#        #Files only has get method. Post are mode from recipes_links, pots ....
#        # I do this test manually
#        file=models.Files()
#        file.mime="image/png"
#        file.content=b"MY FILE CONTENT"
#        file.size=len(file.content)
#        file.user=self.user_testing
#        file.save()
#        
#        tests_helpers.test_cross_user_data(self, self.client_testing, self.client_other, hlu("files", file.id))
#        
#        #Creates a product from a system product to test meals models
#        r=self.client_testing.post("/api/system_products/49/create_product/")
#        product=loads(r.content)
#                
#        tests_helpers.test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/meals/", {
#            "datetime": timezone.now(), 
#            "products": hlu("products", product["data"]), 
#            "amount": 1, 
#        })
#                
#        tests_helpers.test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/pots/", {
#            "name": "My Pot", 
#            "diameter": 1, 
#            "weight": 1, 
#            "height": 1, 
#        })
#        
#        #Test product i don't need to create
#        tests_helpers.test_cross_user_data(self, self.client_testing, self.client_other, hlu("products", product["data"]))
#        #Test recipes_full i don't need to create, 
#        tests_helpers.test_cross_user_data(self, self.client_testing, self.client_other, hlu("recipes_full", recipe["id"]))
#        
#        
#        tests_helpers.test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/recipes_links/", {
#            "description": "My recipe link", 
#            "type":hlu("recipeslinkstypes", 1) , 
#            "recipes": hlu("recipes", recipe["id"]), 
#            "content": None, 
#        })
#                
#        tests_helpers.test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/elaborationsproductsinthrough/", {
#            "products": hlu("products", product["data"]), 
#            "amount": 1, 
#            "measures_types": hlu("measurestypes", 1), 
#            "elaborations": hlu("elaborations", elaboration["id"]),
#        })
#        
        
        
