# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Additiverisks(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'additiverisks'


class Additives(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    description = models.TextField()
    additiverisks = models.ForeignKey(Additiverisks, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'additives'



class Biometrics(models.Model):
    datetime = models.DateTimeField(blank=True, null=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    users = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    activity = models.IntegerField(blank=True, null=True)
    weightwish = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'biometrics'


class Companies(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    last = models.DateTimeField()
    obsolete = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'companies'




class Elaboratedproducts(models.Model):
    name = models.TextField(blank=True, null=True)
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    last = models.DateTimeField()
    foodtypes = models.ForeignKey('Foodtypes', models.DO_NOTHING, blank=True, null=True)
    obsolete = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'elaboratedproducts'


class Foodtypes(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'foodtypes'


class Formats(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    products_id = models.IntegerField(blank=True, null=True)
    system_product = models.BooleanField(blank=True, null=True)
    last = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'formats'


class Globals(models.Model):
    global_field = models.TextField(db_column='global', primary_key=True)  # Field renamed because it was a Python reserved word.
    value = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'globals'


class Languages(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'languages'


class Meals(models.Model):
    users = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    products_id = models.IntegerField(blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    system_product = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'meals'


class Personalcompanies(models.Model):
    id = models.AutoField()
    name = models.TextField(blank=True, null=True)
    last = models.DateTimeField()
    obsolete = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'personalcompanies'


class Personalformats(models.Model):
    name = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    products_id = models.IntegerField(blank=True, null=True)
    system_product = models.BooleanField(blank=True, null=True)
    last = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'personalformats'


class Personalproducts(models.Model):
    id = models.AutoField()
    name = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    companies_id = models.IntegerField(blank=True, null=True)
    last = models.DateTimeField()
    elaboratedproducts_id = models.IntegerField(blank=True, null=True)
    calories = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cholesterol = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sodium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    potassium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fiber = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sugars = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    saturated_fat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    languages = models.TextField(blank=True, null=True)  # This field type is a guess.
    system_company = models.BooleanField(blank=True, null=True)
    foodtypes_id = models.IntegerField(blank=True, null=True)
    additives = models.TextField(blank=True, null=True)  # This field type is a guess.
    obsolete = models.BooleanField()
    ferrum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    magnesium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    phosphor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    glutenfree = models.BooleanField()
    calcium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'personalproducts'


class Products(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    protein = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    carbohydrate = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    companies_id = models.IntegerField(blank=True, null=True)
    last = models.DateTimeField()
    elaboratedproducts_id = models.IntegerField(blank=True, null=True)
    calories = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    salt = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cholesterol = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sodium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    potassium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    fiber = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sugars = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    saturated_fat = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    languages = models.TextField(blank=True, null=True)  # This field type is a guess.
    system_company = models.BooleanField(blank=True, null=True)
    foodtypes = models.ForeignKey(Foodtypes, models.DO_NOTHING)
    additives = models.TextField(blank=True, null=True)  # This field type is a guess.
    obsolete = models.BooleanField()
    ferrum = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    magnesium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    phosphor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    glutenfree = models.BooleanField()
    calcium = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products'


class ProductsInElaboratedproducts(models.Model):
    products_id = models.IntegerField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    elaboratedproducts = models.ForeignKey(Elaboratedproducts, models.DO_NOTHING, blank=True, null=True)
    system_product = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'products_in_elaboratedproducts'


class Users(models.Model):
    name = models.TextField(blank=True, null=True)
    starts = models.DateTimeField(blank=True, null=True)
    ends = models.DateTimeField(blank=True, null=True)
    male = models.BooleanField(blank=True, null=True)
    birthday = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'users'
