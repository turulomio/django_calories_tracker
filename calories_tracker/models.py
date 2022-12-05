# There are system_companies, products_companies
# Products have a reference to system_products. Can hava a reference to elaborated_products
# Formats are for all products in a many to many relations
# Meals and elaborated_products reference to products
# If a product has a system_products reference, uses system_products data and sets all values to -1


# La base de datos de system_Products se pone en dolthub y se sincroniza por github o por locals
# Los nuevos system products se meten usango python manage dolt, desde catalogos. y luego se suben al github.
# Si hubiera usuarios que aportan hay que valorar como poner las claves primarias

#CAda vez que se crea un producto, se copia y se linka de system_products si existiera 

from calories_tracker.reusing.datetime_functions import dtaware2string
from datetime import date, timedelta
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User # new
from django.utils.translation import gettext as _

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
    
    ## Returns a json string
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)}, "description": {jss(self.description)}, "multiplier": {jss(self.multiplier)} }}"""
        


class AdditiveRisks(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'additive_risks'
        
    ## Returns a json string
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)} }}"""
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
    ## Returns a json string
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)} }}"""
        
    def __str__(self):
        return self.name

class Additives(models.Model):
    name = models.TextField()
    description = models.TextField()
    additive_risks = models.ForeignKey(AdditiveRisks, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'additives'
        
    ## Returns a json string
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)}, "description": {jss(self.description)}, "additive_risks": {jss(self.additive_risks.id)} }}"""
    
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
        
    def fullname(self):
        return f"{self.name}: {self.description}"
    
def get_profile(user):
    try:
        return user.profiles
    except:
        profile=Profiles()
        profile.birthday=date(1900, 1, 1)
        profile.male=True
        profile.user=user
        profile.save()
        return profile
    
class Biometrics(models.Model):
    datetime = models.DateTimeField()
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
    
    ##basal metabolic rate
    def bmr(self):
        if hasattr(self, "_bmr") is False:
            profile=get_profile(self.user)
            if profile.male is True:
                self._bmr= self.activities.multiplier*(Decimal(10)*self.weight + Decimal(6.25)*self.height - Decimal(5)*profile.age() + 5)
            else: #female
                self._bmr= self.activities.multiplier*(Decimal(10)*self.weight + Decimal(6.25)*self.height - Decimal(5)*profile.age() - 161)
        return self._bmr

    ##    https://www.healthline.com/nutrition/how-much-protein-per-day#average-needs
    ## If you’re at a healthy weight, don't lift weights and don't exercise much, then aiming for 0.36–0.6 grams per pound (0.8–1.3 gram per kg) is a reasonable estimate.
    ##
    ##This amounts to:
    ##
    ##56–91 grams per day for the average male.
    ##46–75 grams per day for the average female.
    ##
    ## But given that there is no evidence of harm and a significant evidence of benefit, it’s likely better for most people to err on the side of more protein rather than less.
    def recommended_protein(self):
        return self.bmr()*Decimal(0.175)/Decimal(4)


    ## The Mediterranean diet includes a wide variety of plant and animal foods such as fish, meat, eggs, dairy, extra virgin olive oil, fruits, vegetables, legumes and whole grains.
    ## 
    ## It typically provides 35–40% of calories from fat, including plenty of monounsaturated fat from olive oil.
    ##
    ## Here are a few examples of suggested daily fat ranges for a Mediterranean diet, based on different calorie goals:
    ##
    ##     1,500 calories: About 58–67 grams of fat per day.
    ##     2,000 calories: About 78–89 grams of fat per day.
    ##     2,500 calories: About 97–111 grams of fat per day.
    ## Segun https://www.tuasaude.com/es/calorias-de-los-alimentos/ cada gramo grasa tiene 9 calorias
    ## 60% hidratos, 17.5% proteínas y 22.5% de grasas. SERA SELECCIONABLE
    def recommended_fat(self):
        return self.bmr()*Decimal(0.225)/Decimal(9)

    def recommended_carbohydrate(self):
        return self.bmr()*Decimal(0.60)/Decimal(4)
        
    ## Recomendación de la OMS para el consumo de azúcar
    ## Pronto hará tres años que la Organización Mundial de la Salud (OMS) publicó un documento con recomendaciones y directrices sobre el consumo de azúcar en adultos y niños, y lo dejó bien claro:
    ## Tanto para los adultos como para los niños, el consumo de azúcares libres se debería reducir a menos del 10% de la ingesta calórica total. Una reducción por debajo del 5% de la ingesta calórica total produciría beneficios adicionales para la salud.”
    def recommended_sugars(self):
        return self.bmr()*Decimal(0.05)/Decimal(4)


    def recommended_fiber(self):
        return Decimal(25)
        
    def recommended_sodium(self):
        return Decimal(2400)

    # Índice de masa corporal
    def imc(self):
        return self.weight/((self.height/100)**2)
    
    ## https://www.seedo.es/index.php/pacientes/calculo-imc
    def imc_comment(self):
        imc=self.imc()
        if imc <18.5:
            return "Peso insuficiente"
        elif imc<24.9:
            return "Peso normal"
        elif imc<26.9:
            return "Sobrepeso grado I"
        elif imc<29.9:
            return "Sobrepeso grado II (preobesidad)"
        elif imc<34.9:
            return "Obesidad grado I"
        elif imc<39.9:
            return "Obesidad grado II"
        elif imc<50:
            return "Obesidad grado III (mórbida)"
        elif imc>=50:
            return "Obesidad grado IV (extrema)"

class FoodTypes(models.Model):
    name = models.TextField(blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'food_types'
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True
    ## Returns a json string
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)} }}"""
        
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
    ## Returns a json string
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)}, "last": {jss(self.last)}, "obsolete": {jss(self.obsolete)} }}"""
        
    def __str__(self):
        return self.name
                
    ## @param sp SystemProducts to link to Product
    ## Solo debe usarse cuando se linke o se sepa que es un systemproduct
    def update_linked_company(self, user):
        #Search for system_productst in Products
        qs=Companies.objects.filter(system_companies=self, user=user)
        if len(qs)==0: # Product must be created
            p=Companies()
        else:
            p=qs[0]
            
        p.name=self.name
        p.last=self.last
        p.obsolete=self.obsolete
        p.system_companies=self
        p.user=user
        p.save()
        return p

class Companies(models.Model):
    name = models.TextField()
    last = models.DateTimeField(auto_now_add=True)
    obsolete = models.BooleanField()
    system_companies = models.ForeignKey(SystemCompanies, on_delete=models.DO_NOTHING,  blank=True, null=True) # Can be none

    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    class Meta:
        managed = True
        db_table = 'companies'
        
    def __str__(self):
        return self.name
        
    def is_editable(self):
        if self.system_companies is None:
            return True
        return False
        
    def is_deletable(self):
        if self.uses()>0:
            return False
        return True


class Formats(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'formats'
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True
        
    ## Returns a json string
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)} }}"""

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
    formats = models.ManyToManyField(Formats, through='SystemProductsFormatsThrough', blank=True)
    density=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    obsolete = models.BooleanField()
    
    version_parent=models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)
    version= models.DateTimeField()
    version_description=models.TextField(blank=True, null=True)

    ## Returns a json string
    def json(self):
        system_companies=None if self.system_companies is None else self.system_companies.id
        food_types=None if self.food_types is None else self.food_types.id
        version_parent=None if self.version_parent is None else self.version_parent.id
        
        additives=""
        for a in self.additives.all().order_by("id"):#Son objetos additives
            additives=additives+f"""{{ "additives": {jss(a.id)} }},"""
        additives=additives[:-1]
        
        formats=""
        for spf in self.systemproductsformatsthrough_set.all().order_by("id"):#Son objetos additives
            formats=formats+f"""{{ "id": {jss(spf.id)}, "formats": {jss(spf.formats.id)}, "amount": {jss(spf.amount)} }},"""
        formats=formats[:-1]
        
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)}, "amount": {jss(self.amount)}, "fat": {jss(self.fat)}, "protein": {jss(self.protein)}, "carbohydrate": {jss(self.carbohydrate)}, "calories": {jss(self.calories)}, "salt": {jss(self.salt)}, "cholesterol": {jss(self.cholesterol)}, "sodium": {jss(self.sodium)}, "potassium": {jss(self.potassium)}, "fiber": {jss(self.fiber)}, "sugars": {jss(self.sugars)}, "saturated_fat": {jss(self.saturated_fat)}, "ferrum": {jss(self.ferrum)}, "magnesium": {jss(self.magnesium)}, "phosphor": {jss(self.phosphor)}, "glutenfree": {jss(self.glutenfree)}, "calcium": {jss(self.calcium)}, "system_companies": {jss(system_companies)}, "food_types": {jss(food_types)}, "obsolete": {jss(self.obsolete)}, "version_parent": {jss(version_parent)}, "version": {jss(self.version)}, "version_description": {jss(self.version_description)}, "additives" : [{additives}], "formats": [{formats}] }}"""


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
        if not self.density==other.density:
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
        return self.fullname()
        
    def fullname(self):
        company=""
        if self.system_companies is not None:
            company=f" ({self.system_companies.name})"
        version_parent=""
        if self.version_parent is not None:
            version_parent=f" v{self.version.date()}"
        
        
        return f"{_(self.name)}{company}{version_parent}"
        
        
                
    ## @param sp SystemProducts to link to Product
    ## Solo debe usarse cuando se linke o se sepa que es un systemproduct
    def update_linked_product(self, user):
        #Search for system_productst in Products
        qs=Products.objects.filter(system_products=self, user=user)
        if len(qs)==0: # Product must be created
            p=Products()
        else:
            p=qs[0]
            
        p.name=self.name
        p.amount=self.amount
        p.fat=self.fat
        p.protein=self.protein
        p.carbohydrate=self.carbohydrate
        p.calories=self.calories
        p.salt=self.salt
        p.cholesterol=self.cholesterol
        p.sodium=self.sodium
        p.potassium=self.potassium
        p.fiber=self.fiber
        p.sugars=self.sugars
        p.saturated_fat=self.saturated_fat
        p.ferrum=self.ferrum
        p.magnesium=self.magnesium
        p.phosphor=self.phosphor
        p.glutenfree=self.glutenfree
        p.calcium=self.calcium
        p.density=self.density
        p.system_products=self
        p.elaborated_products=None
        p.food_types=self.food_types
        p.obsolete=self.obsolete
        if self.system_companies is not None:
            p.companies=self.system_companies.update_linked_company(user)
        if self.version_parent is not None:
            p.version_parent=self.version_parent.update_linked_product(user)
        p.version=self.version
        p.version_description=self.version_description
        p.user=user
        p.save()

        p.additives.set(self.additives.all())
        p.save()
        
        ## Delete old formats
        ProductsFormatsThrough.objects.filter(products=p).delete()
        
        ## Refresh system products formats
        for f in self.formats.all():
            spft=SystemProductsFormatsThrough.objects.get(system_products=self, formats=f)
            
            

            th=ProductsFormatsThrough()
            th.amount=spft.amount
            th.formats=spft.formats
            th.products=p
            
            th.save()
            
        p.save()
        return p
        
    @staticmethod
    def update_all_linked_products( user):
        
            ## Gets system_companies_id already in companies
            system_products_ids_in_products=Products.objects.filter(user=user, system_products__isnull=False).values("system_products_id")
            ## Filter by name and exclude already
            qs=SystemProducts.objects.filter(id__in=system_products_ids_in_products)
            for sp in qs:
                sp.update_linked_product(user)
                
    def additives_risk(self):
        r=0
        for a in self.additives.all():
            if a.additive_risks.id>r:
                r=a.additive_risks.id
                
        return r

class SystemProductsFormatsThrough(models.Model):
    system_products = models.ForeignKey(SystemProducts, on_delete=models.DO_NOTHING)
    formats = models.ForeignKey(Formats, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=3)

        
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
    additives = models.ManyToManyField(Additives, blank=True, related_name="additives")
    density=models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
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
        return self.fullname()
        
    def fullname(self):
        company=""
        if self.companies is not None:
            company=f" ({self.companies.name})"
        version_parent=""
        if self.version_parent is not None:
            version_parent=f" v{self.version.date()}"
        
        
        return f"{_(self.name)}{company}{version_parent}"
        
    def additives_risk(self):
        r=0
        for a in self.additives.all():
            if a.additive_risks.id>r:
                r=a.additive_risks.id
                
        return r
        

    ## name can be, fat, saturated_fat, fiber, sodiumm...
    def getProductComponentIn100g(self, name, decimals=2):
        component=getattr(self, name)
        if component is None or self.amount==0:
            return None
        return component*100/self.amount

class ProductsFormatsThrough(models.Model):
    products = models.ForeignKey(Products, on_delete=models.DO_NOTHING)
    formats = models.ForeignKey(Formats, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=3)


    def is_editable(self):
        if self.products.system_products is None:
            return True
        return False
        
    def is_deletable(self):
        if self.products.system_products is None:
            return True
        return False

class ElaboratedProducts(models.Model):
    name = models.TextField()
    final_amount = models.DecimalField(max_digits=10, decimal_places=3)
    last = models.DateTimeField(auto_now_add=True)
    food_types = models.ForeignKey(FoodTypes, models.DO_NOTHING)
    obsolete = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    products_in = models.ManyToManyField(Products, through='ElaboratedProductsProductsInThrough', blank=True)
    recipes= models.ForeignKey("Recipes", models.DO_NOTHING, null=True, blank=True)

    class Meta:
        managed = True
        db_table = 'elaborated_products'
        
    def __str__(self):
        return self.name

    def is_deletable(self):
        if self.uses() >0:
            return False
        return True
        
    def get_products_in(self):
        if not hasattr(self, "_products_in") :
            self._products_in=ElaboratedProductsProductsInThrough.objects.select_related("products").prefetch_related("products__additives__additive_risks").filter(elaborated_products=self)
        return self._products_in


    def is_glutenfree(self):
        for pi in self.get_products_in():
            if pi.products.glutenfree is False:
                return False
        return True

    def update_associated_product(self):
        qs=Products.objects.filter(elaborated_products=self, user=self.user)
        if len(qs)==0: #Doesn't exist
            p=Products()
        else:
            p=qs[0]
                    
        p.name=self.name
        p.elaborated_products=self
        p.amount=100
        p.glutenfree=self.is_glutenfree()
        p.obsolete=self.obsolete
        p.food_types=self.food_types
        p.user=self.user
        
        p.calories=self.getElaboratedProductComponent("calories")
        p.fat=self.getElaboratedProductComponent("fat")
        p.protein=self.getElaboratedProductComponent("protein")
        p.carbohydrate=self.getElaboratedProductComponent("carbohydrate")
        p.calories=self.getElaboratedProductComponent("calories")
        p.salt=self.getElaboratedProductComponent("salt")
        p.cholesterol=self.getElaboratedProductComponent("cholesterol")
        p.sodium=self.getElaboratedProductComponent("sodium")
        p.potassium=self.getElaboratedProductComponent("potassium")
        p.fiber=self.getElaboratedProductComponent("fiber")
        p.sugars=self.getElaboratedProductComponent("sugars")
        p.saturated_fat=self.getElaboratedProductComponent("saturated_fat")
        p.ferrum=self.getElaboratedProductComponent("ferrum")
        p.magnesium=self.getElaboratedProductComponent("magnesium")
        p.phosphor=self.getElaboratedProductComponent("phosphor")
        p.calcium=self.getElaboratedProductComponent("calcium")
        p.save()
        return p
        
    ## name can be, fat, saturated_fat, fiber, sodiumm...
    ## @param if Total==False gives component in 100 gramos, else givves component in final_amount gramos
    def getElaboratedProductComponent(self, name, total=False):
        all_pi_component=0
        for pi in self.get_products_in():
            pi_product_amount=pi.products.amount
            pi_product_component=getattr(pi.products, name)
            if pi_product_component is None or pi_product_amount==0:
                return None
            all_pi_component=all_pi_component+ pi.amount*pi_product_component/pi_product_amount
            
        if total is True:
            return all_pi_component
        else:
            return 100*all_pi_component/self.final_amount     
            
    def additives_risk(self):
        r=0
        for pi in self.get_products_in():
            ar=pi.products.additives_risk()
            if ar>r:
                r=ar
        return r

class ElaboratedProductsProductsInThrough(models.Model):
    products = models.ForeignKey(Products, on_delete=models.DO_NOTHING)
    elaborated_products = models.ForeignKey(ElaboratedProducts, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=3)


class Meals(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    products = models.ForeignKey(Products, models.DO_NOTHING)
    datetime = models.DateTimeField()

    class Meta:
        managed = True
        db_table = 'meals'

    def __str__(self):
        return f"{self.products} ({self.amount}g)"
        
    ## name can be, fat, saturated_fat, fiber, sodiumm...
    def getProductComponent(self, name, decimals=2):
        component=getattr(self.products, name)
        if component is None or self.products.amount==0:
            return None
        return self.amount*component/self.products.amount
        
## Pots and pans
class Pots(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=False, null=False)
    name = models.TextField( blank=False, null=False)
    weight = models.IntegerField( blank=False, null=False)#g
    diameter = models.IntegerField( blank=False, null=False)#cm

    class Meta:
        managed = True
        db_table = 'pots'

    def __str__(self):
        self.fullname()
        
    def fullname(self):
        return f"{self.name} ({self.diameter}cm, {self.weight}g)"
        

class Profiles(models.Model):
    male = models.BooleanField()
    birthday = models.DateField()
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING,primary_key=True,)

    class Meta:
        managed = True
        db_table = 'profiles'


    def age(self):
        return (date.today() - self.birthday) // timedelta(days=365.2425)
        
    
class RecipesCategories(models.Model):
    name=models.TextField( blank=False, null=False)
    
    class Meta:
        managed = True
        db_table = 'recipes_categories'
    
    def __str__(self):
        return self.name
        
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)} }}"""
        
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True

class Recipes(models.Model):
    name = models.TextField()
    last = models.DateTimeField(auto_now_add=True)
    food_types = models.ForeignKey(FoodTypes, models.DO_NOTHING)
    obsolete = models.BooleanField()
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    comment=models.TextField( blank=True, null=True)
    valoration=models.IntegerField(blank=True, null=True)
    guests=models.BooleanField(blank=False, null=False)
    soon=models.BooleanField(blank=False, null=False)
    recipes_categories = models.ManyToManyField(RecipesCategories, blank=True)
    class Meta:
        managed = True
        db_table = 'recipes'
    
class RecipesLinksTypes(models.Model):
    name=models.TextField( blank=False, null=False)
    class Meta:
        managed = True
        db_table = 'recipes_links_types'
    def __str__(self):
        return self.name
        ## Returns a json string
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)} }}"""
        
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True

class RecipesLinks(models.Model):
    description=models.TextField( blank=False, null=False)
    type=models.ForeignKey(RecipesLinksTypes, models.DO_NOTHING)
    link=models.TextField( blank=False, null=True)
    content=models.BinaryField( blank=False, null=True)
    recipes=models.ForeignKey(Recipes, related_name="recipes_links", on_delete=models.DO_NOTHING) 
    mime=models.TextField( blank=False, null=True)
    class Meta:
        managed = True
        db_table = 'recipes_links'
    
    
class Elaborations(models.Model):
    diners = models.IntegerField( blank=False, null=False)
    elaborations_products_in = models.ManyToManyField(Products, through='ElaborationsProductsInThrough', blank=True)
    recipes=models.ForeignKey(Recipes, related_name="elaborations", on_delete=models.DO_NOTHING) 
    final_amount = models.DecimalField(max_digits=10, decimal_places=3)
    
    class Meta:
        managed = True
        db_table = 'elaborations'
        
    def __str__(self):
        return f"Elaborations: {self.recipes.name} {self.diners}"
    
class MeasuresTypes(models.Model):
    name=models.TextField( blank=False, null=False)
    class Meta:
        managed = True
        db_table = 'measures_types'
    def __str__(self):
        return self.name
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)} }}"""
        
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True


class ElaborationsProductsInThrough(models.Model):
    products = models.ForeignKey(Products, on_delete=models.DO_NOTHING)
    elaborations = models.ForeignKey(Elaborations, on_delete=models.DO_NOTHING)
    measures_types = models.ForeignKey(MeasuresTypes, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    
    def __str__(self):
        return f"EPT: {self.products.name} {self.elaborations}"
        
        
    def final_grams(self):
        ## Calcula los gramos partiendo de la densidad
        ## Si no hay densidad devuelve los gramos con un warning
        if self.id==1:#Grams
            return self.amount
        elif self.id>=2:#Milliliters
            if self.products.density is None:
                print(_("Density of {0} is null").format(self.products.name))
                return self.amount
            return self.products.density*self.amount

class TemperaturesTypes(models.Model):
    name=models.TextField( blank=False, null=False)
    class Meta:
        managed = True
        db_table = 'temperatures_types'
    def __str__(self):
        return self.name
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)} }}"""
        
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True

class StirTypes(models.Model):
    name=models.TextField( blank=False, null=False)
    

    class Meta:
        managed = True
        db_table = 'stir_types'
    def __str__(self):
        return self.name
    def json(self):
        return f"""{{ "id": {jss(self.id)}, "name": {jss(self.name)} }}"""
        
    def is_fully_equal(self, other):
        if not self.name==other.name:
            return False
        return True

class Steps(models.Model):
    name=models.TextField( blank=False, null=False)
    class Meta:
        managed = True
        db_table = 'steps'
    def __str__(self):
        return f"Step: {self.name}"
    
class ElaborationsContainers(models.Model):
    name=models.TextField( blank=False, null=False)
    elaborations = models.ForeignKey(Elaborations, related_name="elaborations_containers", on_delete=models.CASCADE)
    
    class Meta:
        managed = True
        db_table = 'elaborations_containers'

    def __str__(self):
        return self.name
        
##Una clase con muchas opciones que en el front se esconderán dependiendo del step
class ElaborationsSteps(models.Model):
    order=models.IntegerField(blank=False, null=False)
    elaborations = models.ForeignKey(Elaborations, related_name="elaborations_steps", on_delete=models.DO_NOTHING)
    steps=models.ForeignKey(Steps, on_delete=models.DO_NOTHING)
    duration=models.TimeField(blank=False, null=False)
    comment=models.TextField( blank=True, null=True)
    products_in_step = models.ManyToManyField(ElaborationsProductsInThrough, blank=True, related_name="products_in_step")
    container=models.ForeignKey(ElaborationsContainers, related_name="container", on_delete=models.DO_NOTHING, blank=True, null=True)
    container_to=models.ForeignKey(ElaborationsContainers, related_name="container_to", on_delete=models.DO_NOTHING, blank=True, null=True)
    
    ## Temperatures types can be
    ## - Celsius degrees (1) => Temperature values (value)
    ## - Low / Medium / High => Temperature values (-1,-2, -3)
    ## Para poner temperatura ambiente Temperature types = None
    temperatures_types=models.ForeignKey(TemperaturesTypes, on_delete=models.DO_NOTHING, blank=True, null=True)
    temperatures_values=models.IntegerField(blank=True, null=True)
    stir_types=models.ForeignKey(StirTypes, on_delete=models.DO_NOTHING, blank=True, null=True)
    stir_values=models.IntegerField(blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'elaborations_steps'

class ElaborationsExperiences(models.Model):
    datetime = models.DateTimeField(blank=False, null=False)
    experience=models.TextField( blank=False, null=False)
    elaborations = models.ForeignKey(Elaborations, related_name="elaborations_experiences", on_delete=models.CASCADE)
    
    class Meta:
        managed = True
        db_table = 'elaborations_experiences'

    def __str__(self):
        return self.name


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
## Converts a value to a json strings, depending its value
## str >> "str"

def jss(value):
    if value is None:
        return "null"
    elif value.__class__.__name__=="str":
        return f'"{value}"'
    elif value.__class__.__name__ in ("int", "float", "Decimal"):
        return f"{value}"
    elif value.__class__.__name__=="time":
        return f'"{value}"'
    elif value.__class__.__name__=="bool":
        return f"{str(value).lower()}"
    elif value.__class__.__name__=="datetime":
        return f'"{dtaware2string(value, "JsUtcIso")}"'
    else:
        print(f"Rare value '{value}' ({value.__class__.__name__}) in jss")
