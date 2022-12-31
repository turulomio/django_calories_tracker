from calories_tracker.tests_helpers import hlu, call_command_sqlsequencerreset, test_cross_user_data, print_list
from django.contrib.auth.models import User
from django.core.management import call_command
from django.utils import timezone
from json import loads
from rest_framework.test import APIClient, APITestCase

print_list    

class LoginTestCase(APITestCase):

    def setUp(self):
        # Call necessary commands
        call_command("update_catalogs")
        call_command_sqlsequencerreset("calories_tracker")
        
        # User to test api
        user_testing = User(
            email='testing@testing.com',
            first_name='Testing',
            last_name='Testing',
            username='testing',
        )
        user_testing.set_password('testing123')
        user_testing.save()
        
        # User to confront security
        user_other = User(
            email='other@other.com',
            first_name='Other',
            last_name='Other',
            username='other',
        )
        user_other.set_password('other123')
        user_other.save()
        
        client = APIClient()
        response = client.post('/login/', {'username': user_testing.username, 'password': 'testing123',},format='json')
        result = loads(response.content)
        self.token_user_testing = result
        
        response = client.post('/login/', {'username': user_other.username, 'password': 'other123',},format='json')
        result = loads(response.content)
        self.token_user_other = result
        
        self.client_testing=APIClient()
        self.client_testing.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user_testing)
        self.client_other=APIClient()
        self.client_other.credentials(HTTP_AUTHORIZATION='Token ' + self.token_user_other)
        
        
    def test_cross_user_data(self):
        test_cross_user_data(self, self.client_testing, self.client_other, "/api/biometrics/", {
            "datetime": timezone.now(), 
            "weight": 71, 
            "height": 180, 
            "activities": hlu("activities", 0), 
            "weight_wishes": hlu("weightwishes", 0)
        })
        test_cross_user_data(self, self.client_testing, self.client_other, "/api/companies/", {
            "name": "My company", 
            "obsolete":False, 
        })
        test_cross_user_data(self, self.client_testing, self.client_other, "/api/elaborated_products/", {
            "name": "My elaborated product", 
            "final_amount":1111, 
            "food_types": hlu("foodtypes", 1), 
            "obsolete": False, 
            "products_in": []
        })
        print_list(self.client_testing, "/api/companies/")
