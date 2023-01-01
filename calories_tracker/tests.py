from calories_tracker import models
from calories_tracker.tests_helpers import hlu, test_cross_user_data, test_cross_user_data_with_post, print_list
from django.contrib.auth.models import User
from django.utils import timezone
from json import loads
from rest_framework.test import APIClient, APITestCase
print_list    

class CtTestCase(APITestCase):
    fixtures=["all.json"]
    catalog_tables=["activities", "additives", "additive_risks"]

    def setUp(self):
        """
            Executed on each test case instance
        """ 
        client = APIClient()
        response = client.post('/login/', {'username': self.user_testing.username, 'password': 'testing123',},format='json')
        result = loads(response.content)
        self.token_user_testing = result
        
        response = client.post('/login/', {'username': self.user_other.username, 'password': 'other123',},format='json')
        result = loads(response.content)
        self.token_user_other = result
        
        self.client_testing=APIClient()
        self.client_testing.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user_testing)

        self.client_other=APIClient()
        self.client_other.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user_other)
        


    @classmethod
    def setUpClass(cls):
        """
            Only instantiated once
        """
        print("SETUP")
        super().setUpClass()
        # Call necessary commands
#        call_command("update_catalogs")
#        call_command_sqlsequencerreset("calories_tracker")
        
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
        print("SETUP END")

    def test_catalog_tables_only_get(self):
        print("NOW")
        """
            Checks that catalog table can be only accesed to GET method to normal users
        """
        for catalog in self.catalog_tables:
            self.client_testing.post(f"/api/{catalog}", {})
        
        
    def test_cross_user_models_security(self):
        """
            Checks that a user can't see other user registers
        """
        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/biometrics/", {
            "datetime": timezone.now(), 
            "weight": 71, 
            "height": 180, 
            "activities": hlu("activities", 0), 
            "weight_wishes": hlu("weightwishes", 0)
        })
        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/companies/", {
            "name": "My company", 
            "obsolete":False, 
        })
        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/elaborated_products/", {
            "name": "My elaborated product", 
            "final_amount":1111, 
            "food_types": hlu("foodtypes", 1), 
            "obsolete": False, 
            "products_in": []
        })
        recipe=test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/recipes/", {
            "name": "My recipe", 
            "final_amount":1111, 
            "food_types": hlu("foodtypes", 1), 
            "obsolete": False, 
            "comment": None,
            "valoration": 99,
            "guests": True, 
            "soon": True, 
        })
        
        elaboration=test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/elaborations/", {
            "diners": 4, 
            "final_amount":1111, 
            "recipes": hlu("recipes", recipe["id"]),
        })

        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/elaborations_containers/", {
            "name": "My elaboration container", 
            "elaborations": hlu("elaborations", elaboration["id"]),
        })
        
        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/elaborations_experiences/", {
            "datetime": timezone.now(), 
            "experience": "My elaboration experience", 
            "elaborations": hlu("elaborations", elaboration["id"]),
        })
        
        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/elaborations_steps/", {
            "duration": "00:01:00", 
            "order": 1, 
            "elaborations": hlu("elaborations", elaboration["id"]),
            "steps": hlu("steps", 2),
        })
        
        #Files only has get method. Post are mode from recipes_links, pots ....
        # I do this test manually
        file=models.Files()
        file.mime="image/png"
        file.content=b"MY FILE CONTENT"
        file.size=len(file.content)
        file.user=self.user_testing
        file.save()
        
        test_cross_user_data(self, self.client_testing, self.client_other, hlu("files", file.id))
        
        #Creates a product from a system product to test meals models
        r=self.client_testing.post("/api/system_products/49/create_product/")
        product=loads(r.content)
                
        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/meals/", {
            "datetime": timezone.now(), 
            "products": hlu("products", product["data"]), 
            "amount": 1, 
        })
                
        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/pots/", {
            "name": "My Pot", 
            "diameter": 1, 
            "weight": 1, 
            "height": 1, 
        })
        
        #Test product i don't need to create
        test_cross_user_data(self, self.client_testing, self.client_other, hlu("products", product["data"]))
        #Test recipes_full i don't need to create, 
        test_cross_user_data(self, self.client_testing, self.client_other, hlu("recipes_full", recipe["id"]))
        
        
        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/recipes_links/", {
            "description": "My recipe link", 
            "type":hlu("recipeslinkstypes", 1) , 
            "recipes": hlu("recipes", recipe["id"]), 
            "content": None, 
        })
                
        test_cross_user_data_with_post(self, self.client_testing, self.client_other, "/api/elaborationsproductsinthrough/", {
            "products": hlu("products", product["data"]), 
            "amount": 1, 
            "measures_types": hlu("measurestypes", 1), 
            "elaborations": hlu("elaborations", elaboration["id"]),
        })
        
        
        
