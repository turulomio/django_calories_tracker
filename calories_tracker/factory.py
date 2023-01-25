#from django.contrib.auth.models import User
from factory import Faker, SubFactory, lazy_attribute, post_generation
from factory.django import DjangoModelFactory
#from django.contrib.auth.hashers import make_password
from calories_tracker import models
from django.utils import timezone
#https://faker.readthedocs.io/en/master/providers/faker.providers.currency.html

#
#class UserFactory(DjangoModelFactory):
#    class Meta:
#        model = User
#
#    first_name = "Sophia"
#    last_name = "Ball"
#    username = "clowngirl@heaven.com"
#    password = make_password("CHANGEME")
#    email = "clowngirl@heaven.com"
#    is_active = True

class FoodTypesFactory(DjangoModelFactory):
    class Meta:
        model= models.FoodTypes
        
    name = Faker("bothify", text="Food Type ??????")

class RecipesCategoriesFactory(DjangoModelFactory):
    class Meta:
        model= models.RecipesCategories
        
    name = Faker("bothify", text="Recipe Category ??????")
    
class RecipesLinksTypesFactory(DjangoModelFactory):
    class Meta:
        model= models.RecipesLinksTypes
        
    name = Faker("bothify", text="Recipe Link Type ??????")




class RecipesFactory(DjangoModelFactory):
    class Meta:
        model= models.Recipes
    name = Faker("bothify", text="Recipe ??????")
    datetime=timezone.now()
    last=timezone.now()
    food_types=SubFactory(FoodTypesFactory)
    obsolete =Faker("boolean")
#    user=SubFactory(UserFactory)
    comment=Faker("sentence")
    valoration=Faker("random_int")
    guests=Faker("boolean")
    soon=Faker("boolean")

    @post_generation
    def recipes_categories(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        # Add the iterable of groups using bulk addition
        self.recipes_categories.add(*extracted)

class RecipesLinksFactory(DjangoModelFactory):
    class Meta:
        model= models.RecipesLinks
        
    description = Faker("bothify", text="Recipe Link ??????")
    type=SubFactory(RecipesLinksTypesFactory)
    link=Faker("uri")
    files=None
    recipes=SubFactory(RecipesFactory)

class ElaboratedProductsFactory(DjangoModelFactory):
    class Meta:
        model= models.ElaboratedProducts
        
    name = Faker("bothify", text="Elaborated Product ??????")
    
    final_amount = Faker("random_int")
    last=timezone.now()
    food_types=SubFactory(FoodTypesFactory)
    obsolete =Faker("boolean")
#    user=SubFactory(UserFactory)
    products_in=None
    recipes=None
    
    @lazy_attribute
    def name(self):
        return f'Leverage x{self.multiplier}'
        
