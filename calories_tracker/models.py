# There are system_companies, products_companies
# Products have a reference to system_products. Can hava a reference to elaborated_products
# Formats are for all products in a many to many relations
# Meals and elaborated_products reference to products
# If a product has a system_products reference, uses system_products data and sets all values to -1

from django.db import models
from django.contrib.auth.models import User # new

class Activities(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'activities'

class AdditiveRisks(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'additive_risks'
        
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True

class WeightWishes(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'weight_wishes'

class Additives(models.Model):
    name = models.TextField()
    description = models.TextField()
    additive_risks = models.ForeignKey(AdditiveRisks, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'additives'

class Biometrics(models.Model):
    datetime = models.DateTimeField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    activities = models.ForeignKey(Activities, on_delete=models.DO_NOTHING) 
    weight_wishes = models.ForeignKey(WeightWishes, on_delete=models.DO_NOTHING) 

    class Meta:
        managed = True
        db_table = 'biometrics'

class FoodTypes(models.Model):
    name = models.TextField(blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'food_types'

class SystemCompanies(models.Model):
    name = models.TextField(blank=True, null=True)
    last = models.DateTimeField()
    obsolete = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'system_companies'

class Companies(models.Model):
    name = models.TextField(blank=True, null=True)
    last = models.DateTimeField()
    obsolete = models.BooleanField()
    system_companies = models.ForeignKey(SystemCompanies, on_delete=models.DO_NOTHING,  blank=True, null=True) # Can be none

    class Meta:
        managed = True
        db_table = 'companies'

class SystemProducts(models.Model):
    name = models.TextField(blank=False, null=False)
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    fat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    calories = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    salt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cholesterol = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sodium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    potassium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fiber = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sugars = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    saturated_fat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ferrum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    magnesium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    phosphor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    glutenfree = models.BooleanField(blank=False, null=False)
    calcium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    system_companies = models.ForeignKey(SystemCompanies, models.DO_NOTHING, blank=False, null=False)
    food_types = models.ForeignKey(FoodTypes, models.DO_NOTHING)
    additives = models.ManyToManyField(Additives)
    obsolete = models.BooleanField()
    
    version_parent=models.ForeignKey("self", models.DO_NOTHING, blank=False, null=False)
    version= models.DateTimeField()
    version_description=models.TextField(blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'syste_products'

class Products(models.Model):
    
    name = models.TextField()
    
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    fat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    calories = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)
    salt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cholesterol = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sodium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    potassium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fiber = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sugars = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    saturated_fat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ferrum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    magnesium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    phosphor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    glutenfree = models.BooleanField(blank=False, null=False)
    calcium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    elaborated_products= models.ForeignKey("ElaboratedProducts", models.DO_NOTHING)
    
    food_types = models.ForeignKey(FoodTypes, models.DO_NOTHING)
    additives = models.ManyToManyField(Additives)
    obsolete = models.BooleanField()
    companies = models.ForeignKey(Companies, models.DO_NOTHING, blank=False, null=False)
    version_parent=models.ForeignKey("self", models.DO_NOTHING, blank=False, null=False)
    version= models.DateTimeField()
    version_description=models.TextField(blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'products'



class ElaboratedProducts(models.Model):
    name = models.TextField(blank=True, null=True)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    last = models.DateTimeField()
    food_types = models.ForeignKey(FoodTypes, models.DO_NOTHING)
    obsolete = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 

    class Meta:
        managed = True
        db_table = 'elaborated_products'

class Formats(models.Model):
    name = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    last = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'formats'


class Meals(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    products = models.ForeignKey(Products, models.DO_NOTHING)
    datetime = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'meals'



class ProductsInElaboratedProducts(models.Model):
    products = models.ForeignKey(Products, models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    elaboratedproducts = models.ForeignKey("ElaboratedProducts", models.DO_NOTHING)
    class Meta:
        managed = True
        db_table = 'products_in_elaborated_products'


class Profile(models.Model):
    name = models.TextField(blank=True, null=True)
    starts = models.DateTimeField(blank=True, null=True)
    ends = models.DateTimeField(blank=True, null=True)
    male = models.BooleanField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'profiles'

