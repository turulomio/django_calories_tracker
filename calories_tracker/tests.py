from calories_tracker.reusing import factory_helpers
from django.contrib.auth.models import User
from django.test import tag
from json import loads
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import Group

tag

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


#
#    @tag("current")
#    def test_product(self):
#        """
#            Checks product logic
#        """
#        print()
#        print("test_product")
#        factory_p=self.factories_manager.find(factory.ProductsFactory)
#        #Creates a new product
#        dict_p=factory_helpers.post(self.client_authorized_1, "/api/products/", factory_p.post_payload(self.client_authorized_1), status.HTTP_201_CREATED)
#        print(dict_p)


#        #Products to system products
##        product=td.tmProducts.create(0, self.client_authorized_1)
##        url=f"{product['url']}convert_to_system/"
##        r=self.client_authorized_1.post(url) #Normal user
##        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN,  f"Error @action {url}")
##        r=self.client_catalog_manager.post(url) #CatalogManager user
##        self.assertEqual(r.status_code, status.HTTP_200_OK,  f"Error @action {url}")

    def test_system_product(self):
        """
            Checks system product logic
        """
        print()
        print("test_system_product")
        post_payload={
            'additives': [], 
            'amount': '5320.000', 
            'calcium': '8551.000', 
            'calories': '2190.000', 
            'carbohydrate': '4137.000', 
            'cholesterol': '2453.000', 
            'system_companies': None, 
            'elaborated_products': None, 
            'fat': '1346.000', 
            'ferrum': '9726.000', 
            'fiber': '4615.000', 
            'food_types': 'http://testserver/api/food_types/2/', 
            'formats': [], 
            'glutenfree': False, 
            'magnesium': '2657.000', 
            'name': 'System Product LfFcdY', 
            'obsolete': False, 
            'phosphor': '1095.000', 
            'potassium': '2181.000', 
            'protein': '1631.000', 
            'salt': '7799.000', 
            'saturated_fat': '527.000', 
            'sodium': '8319.000', 
            'sugars': '9859.000', 
            'version': '2023-06-11T05:35:13.673203Z', 
            'version_description': None, 
            'version_parent': None, 
            'density': '670.000'
        }

        
        #Creates a new system product
        dict_sp=factory_helpers.post(self, self.client_catalog_manager, "/api/system_products/", post_payload, status.HTTP_201_CREATED)

        #Client_autenticated_1 creates a product
        factory_helpers.post(self, self.client_authorized_1, dict_sp["url"]+"create_product/", {},  status.HTTP_200_OK)

        #Client_autenticated_2 creates a product
        factory_helpers.post(self, self.client_authorized_2, dict_sp["url"]+"create_product/", {} , status.HTTP_200_OK)
        
        #List of client_authorized_1 products len must be 1
        dict_all_p1=factory_helpers.get(self, self.client_authorized_1, "/api/products/", status.HTTP_200_OK)
        self.assertEqual(len(dict_all_p1), 1)
        
        #List of client_authorized_2 products len must be 1
        dict_all_p2=factory_helpers.get(self, self.client_authorized_2, "/api/products/", status.HTTP_200_OK)
        self.assertEqual(len(dict_all_p2), 1)
#
#    def test_recipes(self):
#        print()
#        print("test_recipes")
#        mf=factory_helpers.MyFactory(factory.RecipesFactory, "Private", "/api/recipes/")
#        recipe=mf.factory.create(user=self.user_authorized_1, recipes_categories=factory.RecipesCategoriesFactory.create_batch(2))
#        recipe
##        print(factory_helpers.serialize(recipe))
##        self.client_authorized_1.post(mf.url,  mf.post_payload(user=self.user_authorized_1))
#
#    def test_recipes_links(self):
#        print()
#        print("test_recipes_links")
#        mf=factory_helpers.MyFactory(factory.RecipesLinksFactory, "Private", "/api/recipes_links/")
#        recipe=self.client_authorized_1.post(mf.url, PostPayload.RecipesLinks(self.user_authorized_1), format="json")
#        self.assertEqual(recipe.status_code, status.HTTP_201_CREATED)
        
        
