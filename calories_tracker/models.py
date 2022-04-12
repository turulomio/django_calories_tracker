# There are system_companies, products_companies
# Products have a reference to system_products. Can hava a reference to elaborated_products
# Formats are for all products in a many to many relations
# Meals and elaborated_products reference to products
# If a product has a system_products reference, uses system_products data and sets all values to -1

from django.db import models
from django.contrib.auth.models import User # new

class Activities(models.Model):
    name = models.TextField()
    description=models.TextField()
    multiplier=models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        managed = True
        db_table = 'activities'
        
    def __str__(self):
        return self.name

    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        if not self.description==other.description:
            return False
        if not self.multiplier==other.multiplier:
            return False
        return True

class AdditiveRisks(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'additive_risks'
        
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True
        
    def __str__(self):
        return self.name

class WeightWishes(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'weight_wishes'
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True
        
    def __str__(self):
        return self.name

class Additives(models.Model):
    name = models.TextField()
    description = models.TextField()
    additive_risks = models.ForeignKey(AdditiveRisks, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'additives'
        
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        if not self.description==other.description:
            return False
        if not self.additive_risks==other.additive_risks:
            return False
        return True
        
    def __str__(self):
        return self.name

class Biometrics(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    activities = models.ForeignKey(Activities, on_delete=models.DO_NOTHING) 
    weight_wishes = models.ForeignKey(WeightWishes, on_delete=models.DO_NOTHING) 

    class Meta:
        managed = True
        db_table = 'biometrics'
    def __str__(self):
        return str(self.datetime)


class FoodTypes(models.Model):
    name = models.TextField(blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'food_types'
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True
        
    def __str__(self):
        return self.name

class SystemCompanies(models.Model):
    name = models.TextField()
    last = models.DateTimeField()
    obsolete = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'system_companies'
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        if not self.last==other.last:
            return False
        if not self.obsolete==other.obsolete:
            return False
        return True
        
    def __str__(self):
        return self.name

class Companies(models.Model):
    name = models.TextField()
    last = models.DateTimeField(auto_now_add=True)
    obsolete = models.BooleanField()
    system_companies = models.ForeignKey(SystemCompanies, on_delete=models.DO_NOTHING,  blank=True, null=True) # Can be none

    class Meta:
        managed = True
        db_table = 'companies'
        
    def __str__(self):
        return self.name

class Formats(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'formats'
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True
        
    def __str__(self):
        return self.name

class SystemProducts(models.Model):
    name = models.TextField(blank=False, null=False)
    
    amount = models.DecimalField(max_digits=10, decimal_places=3, blank=False, null=False)
    fat = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    protein = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    calories = models.DecimalField(max_digits=10, decimal_places=3, blank=False, null=False)
    salt = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    cholesterol = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    sodium = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    potassium = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    fiber = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    sugars = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    saturated_fat = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    ferrum = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    magnesium = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    phosphor = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    glutenfree = models.BooleanField(blank=False, null=False)
    calcium = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    
    system_companies = models.ForeignKey(SystemCompanies, models.DO_NOTHING, blank=True, null=True)
    food_types = models.ForeignKey(FoodTypes, models.DO_NOTHING)
    additives = models.ManyToManyField(Additives, blank=True)
    formats = models.ManyToManyField(Formats, blank=True)
    obsolete = models.BooleanField()
    
    version_parent=models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)
    version= models.DateTimeField()
    version_description=models.TextField(blank=True, null=True)



    class Meta:
        managed = True
        db_table = 'system_products'

    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        if not self.amount==other.amount:
            return False
        if not self.protein==other.protein:
            return False
        if not self.carbohydrate==other.carbohydrate:
            return False
        if not self.calories==other.calories:
            return False
        if not self.salt==other.salt:
            return False
        if not self.cholesterol==other.cholesterol:
            return False
        if not self.sodium==other.sodium:
            return False
        if not self.potassium==other.potassium:
            return False
        return True
        if not self.fiber==other.fiber:
            return False
        if not self.sugars==other.sugars:
            return False
        if not self.saturated_fat==other.saturated_fat:
            return False
        if not self.ferrum==other.ferrum:
            return False
        if not self.magnesium==other.magnesium:
            return False
        if not self.phosphor==other.phosphor:
            return False
        if not self.glutenfree==other.glutenfree:
            return False
        if not self.calcium==other.calcium:
            return False
        if not self.system_companies==other.system_companies:
            return False
        if not self.food_types==other.food_types:
            return False
        if not self.additives==other.additives:
            return False
        if not self.formats==other.formats:
            return False
        if not self.obsolete==other.obsolete:
            return False
        if not self.version_parent==other.version_parent:
            return False
        if not self.version==other.version:
            return False
        
    def __str__(self):
        return self.name
class Products(models.Model):
    
    name = models.TextField()
    
    
    amount = models.DecimalField(max_digits=10, decimal_places=3, blank=False, null=False)
    fat = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    protein = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    calories = models.DecimalField(max_digits=10, decimal_places=3, blank=False, null=False)
    salt = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    cholesterol = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    sodium = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    potassium = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    fiber = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    sugars = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    saturated_fat = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    ferrum = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    magnesium = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    phosphor = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    glutenfree = models.BooleanField(blank=False, null=False)
    calcium = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    
    system_products= models.ForeignKey("SystemProducts", models.DO_NOTHING, null=True, blank=True)
    elaborated_products= models.ForeignKey("ElaboratedProducts", models.DO_NOTHING, null=True, blank=True)
    
    food_types = models.ForeignKey(FoodTypes, models.DO_NOTHING)
    additives = models.ManyToManyField(Additives, blank=True)
    formats = models.ManyToManyField(Formats, through='ProductsFormatsThrough', blank=True)

    obsolete = models.BooleanField()
    companies = models.ForeignKey(Companies, models.DO_NOTHING, blank=True, null=True)
    version_parent=models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)
    version= models.DateTimeField(auto_now_add=True)
    version_description=models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 

    class Meta:
        managed = True
        db_table = 'products'
    def __str__(self):
        return self.name

class ProductsFormatsThrough(models.Model):
    products = models.ForeignKey(Products, on_delete=models.DO_NOTHING)
    formats = models.ForeignKey(Formats, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=3)



class ElaboratedProducts(models.Model):
    name = models.TextField()
    final_amount = models.DecimalField(max_digits=10, decimal_places=3)
    last = models.DateTimeField(auto_now_add=True)
    food_types = models.ForeignKey(FoodTypes, models.DO_NOTHING)
    obsolete = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    products_in = models.ManyToManyField(Products, through='ElaboratedProductsProductsInThrough', blank=True)

    class Meta:
        managed = True
        db_table = 'elaborated_products'
    def __str__(self):
        return self.name


class ElaboratedProductsProductsInThrough(models.Model):
    products = models.ForeignKey(Products, on_delete=models.DO_NOTHING)
    elaborated_products = models.ForeignKey(ElaboratedProducts, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=3)


class Meals(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    products = models.ForeignKey(Products, models.DO_NOTHING)
    datetime = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'meals'

    def __str__(self):
        return f"{self.products} ({self.amount}g)"

class Profiles(models.Model):
    male = models.BooleanField()
    birthday = models.DateField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 

    class Meta:
        managed = True
        db_table = 'profiles'



class eAdditiveRisk:
    NotEvaluated=100
    NoRisk=0
    Low=1
    Medium=2
    High=3

## TMB x 1,2: Poco o ningún ejercicio                     +
##        |                                |       |          |            | TMB x 1,375: Ejercicio ligero (1 a 3 días a la semana) +
##        |                                |       |          |            | TMB x 1,55: Ejercicio moderado (3 a 5 días a la semana)+
##        |                                |       |          |            | TMB x 1,72: Deportista (6 -7 días a la semana)         +
##        |                                |       |          |            | TMB x 1,9: Atleta (Entrenamientos mañana y tarde)
##    Sedentary. If you get minimal or no exercise, multiply your BMR by 1.2.
##    Lightly active. If you exercise lightly one to three days a week, multiply your BMR by 1.375.
##    Moderately active. If you exercise moderately three to five days a week, multiply your BMR by 1.55.
##    Very active. If you engage in hard exercise six to seven days a week, multiply your BMR by 1.725.
##    Extra active. If you engage in very hard exercise six to seven days a week or have a physical job, multiply your BMR by 1.9.
class eActivity:
    Sedentary=0
    LightlyActive=1
    ModeratelyActive=2
    VeryActive=3
    ExtraActive=4
    
class eWeightWish:
    Lose=0
    Mantain=1
    Gain=2
