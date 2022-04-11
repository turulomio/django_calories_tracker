# There are system_companies, products_companies
# Products have a reference to system_products. Can hava a reference to elaborated_products
# Formats are for all products in a many to many relations
# Meals and elaborated_products reference to products
# If a product has a system_products reference, uses system_products data and sets all values to -1

from django.db import models

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
    def __str__(self):
        return self.name


class FoodTypes(models.Model):
    name = models.TextField(blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'food_types'
    def __str__(self):
        return self.name

class SystemCompanies(models.Model):
    name = models.TextField(blank=True, null=True)
    last = models.DateTimeField()
    obsolete = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'system_companies'
    def __str__(self):
        return self.name


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
        db_table = 'system_products'
    def __str__(self):
        return self.name


class Formats(models.Model):
    name = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'formats'
    def __str__(self):
        return self.name

