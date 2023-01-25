from calories_tracker import factory
from calories_tracker.reusing import factory_helpers
from django.contrib.auth.models import User
from django.test import tag
from json import loads, dumps
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.contrib.auth.models import Group

tag

class PostPayload:
    @staticmethod
    def Biometrics(user=None):
        user=User.objects.get(username="catalog_manager") if user is None else user
        o=factory.BiometricsFactory.create(user=user)
        d=factory_helpers.serialize(o)
        o.delete()
        del d["id"]
        del d["url"]
        return d

    @staticmethod
    def Recipes(user=None):
        user=User.objects.get(username="testing") if user is None else user
        o=factory.RecipesFactory.create(user=user)
        d=factory_helpers.serialize(o)
        o.delete()
        del d["id"]
        del d["url"]
        return d

    @staticmethod
    def RecipesLinks(user=None):
        user=User.objects.get(username="testing") if user is None else user
        recipe=factory.RecipesFactory.create(user=user)
        o=factory.RecipesLinksFactory.create(recipes=recipe, files__user=user )
        d=factory_helpers.serialize(o)
        del d["id"]
        del d["url"]
        del d["files"]
        return d

    @staticmethod
    def SystemProducts(user=None, with_format=False):
        """
            Formats are empty
            @param with_format If true adds a systemproductsformatthrough. If false for common factory_helpers testers don't
        """
        user=User.objects.get(username="catalog_manager") if user is None else user
        sp=factory.SystemProductsFactory.create()
        format=factory.FormatsFactory.create()
        if with_format is True:
            factory.SystemProductsFormatsThroughFactory(system_products=sp, formats=format)
        d=factory_helpers.serialize(sp)
        del d["id"]
        del d["url"]
        return d


class CtTestCase(APITestCase):
    fixtures=["all.json"] #Para cargar datos por defecto

    @classmethod
    def setUpClass(cls):
        """
            Only instantiated once
        """
        super().setUpClass()
        
        cls.factories_manager=factory_helpers.MyFactoriesManager()
        cls.factories_manager.append(factory.ActivitiesFactory, "PrivateEditableCatalog", "/api/activities/")
        cls.factories_manager.append(factory.AdditivesFactory, "PrivateEditableCatalog", "/api/additives/")
        cls.factories_manager.append(factory.AdditiveRisksFactory, "PrivateEditableCatalog", "/api/additive_risks/")
        cls.factories_manager.append(factory.BiometricsFactory, "Private", "/api/biometrics/", PostPayload.Biometrics)
        cls.factories_manager.append(factory.FoodTypesFactory, "PrivateEditableCatalog", "/api/food_types/")
        cls.factories_manager.append(factory.FormatsFactory, "PrivateEditableCatalog", "/api/formats/")
        cls.factories_manager.append(factory.RecipesCategoriesFactory, "PrivateEditableCatalog", "/api/recipes_categories/")
        cls.factories_manager.append(factory.RecipesLinksTypesFactory, "PrivateEditableCatalog", "/api/recipes_links_types/")
        cls.factories_manager.append(factory.RecipesFactory, "Private", "/api/recipes/", PostPayload.Recipes)
        cls.factories_manager.append(factory.RecipesLinksFactory, "Private", "/api/recipes_links/", PostPayload.RecipesLinks) 
        cls.factories_manager.append(factory.SystemCompaniesFactory, "PrivateEditableCatalog", "/api/system_companies/")
        cls.factories_manager.append(factory.SystemProductsFactory, "PrivateEditableCatalog", "/api/system_products/", PostPayload.SystemProducts)        
        cls.factories_manager.append(factory.WeightWishesFactory, "PrivateEditableCatalog", "/api/weight_wishes/")

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
        

    @tag("current")
    def test_factory_by_type(self):
        print()
        for f in self.factories_manager:
            print("test_factory_by_type", f.type,  f)
            f.test_by_type(self, self.client_authorized_1, self.client_authorized_2, self.client_anonymous, self.client_catalog_manager)

    @tag("current")
    def test_system_product(self):
        """
            Checks system product logic
        """
        
        pass

    @tag("current")
    def test_recipes(self):
        print()
        print("test_recipes")
        mf=factory_helpers.MyFactory(factory.RecipesFactory, "Private", "/api/recipes/")
        recipe=mf.factory.create(user=self.user_authorized_1, recipes_categories=factory.RecipesCategoriesFactory.create_batch(2))
        recipe
#        print(factory_helpers.serialize(recipe))
#        self.client_authorized_1.post(mf.url,  mf.post_payload(user=self.user_authorized_1))

    @tag("current")
    def test_recipes_links(self):
        print()
        print("test_recipes_links")
        mf=factory_helpers.MyFactory(factory.RecipesLinksFactory, "Private", "/api/recipes_links/")
        recipe=self.client_authorized_1.post(mf.url, PostPayload.RecipesLinks(self.user_authorized_1), format="json")
        self.assertEqual(recipe.status_code, status.HTTP_201_CREATED)
        
        
