# There are system_companies, products_companies
# Products have a reference to system_products. Can hava a reference to elaborated_products
# Formats are for all products in a many to many relations
# Meals and elaborated_products reference to products
# If a product has a system_products reference, uses system_products data and sets all values to -1


# La base de datos de system_Products se pone en dolthub y se sincroniza por github o por locals
# Los nuevos system products se meten usango python manage dolt, desde catalogos. y luego se suben al github.
# Si hubiera usuarios que aportan hay que valorar como poner las claves primarias

#CAda vez que se crea un producto, se copia y se linka de system_products si existiera 

from base64 import b64encode
from calories_tracker import commons
from calories_tracker.reusing.decorators import ptimeit
from datetime import date, timedelta,  datetime
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User # new

from django.urls import reverse
from django.utils.translation import gettext as _
from fractions import Fraction
from humanize import naturalsize
from math import pi, fmod
from mimetypes import guess_extension
from preview_generator.manager import PreviewManager
from re import findall
from simple_history.models import HistoricalRecords

ptimeit

class Files(models.Model):
    content=models.BinaryField(blank=False, null=False)
    size=models.IntegerField(blank=False, null=False)
    thumbnail=models.BinaryField(blank=True, null=True)
    mime=models.TextField(max_length=100, blank=False, null=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING) 
    class Meta:
        managed = True
        db_table = 'files'
        
    def extension(self):
        r=guess_extension(self.mime)
        return "" if r is None else r
        
    
    def humansize(self):
        return naturalsize(self.size, binary=True)

    
    ##Function to get and create thumbnail if it doesn't exist
    def get_thumbnail(self):
        if self.thumbnail is None or bytes(self.thumbnail)==b"from_migration_i_will_be_regenerated":
            filename=f"{settings.TMPDIR}/files_{self.id}"
            with open(filename, "wb") as f:
                f.write(self.content)

            manager = PreviewManager(settings.TMPDIR_PREVIEW_CACHE, create_folder= False)
            path_to_preview_image = manager.get_jpeg_preview(filename, width=100, height=100, page=0)

            with open(path_to_preview_image, "rb") as f:
                self.thumbnail=f.read()
                self.save()
        return self.thumbnail
 
    def get_b64_thumbnail(self):
        return b64encode(self.get_thumbnail()).decode('UTF-8')
        
    def get_b64_content(self):
        return b64encode(self.content).decode('UTF-8')
        
    #Formato return f"data:{rl.mime};base64,{b64encode(rl.content).decode('UTF-8')}"
    def get_thumbnail_js(self):
        return f"data:image/jpeg;base64,{self.get_b64_thumbnail()}"

    def get_content_js(self):
        return f"data:{self.mime};base64,{self.get_b64_content()}"
        
    def url_thumbnail(self, request):
        return request.build_absolute_uri(reverse('files-detail', args=(self.id, )))+"thumbnail/"

    def url_content(self, request):
        return request.build_absolute_uri(reverse('files-detail', args=(self.id, )))+"content/"
        

class Activities(models.Model):
    name = models.TextField()
    description=models.TextField()
    multiplier=models.DecimalField(max_digits=10, decimal_places=4)

    class Meta:
        managed = True
        db_table = 'activities'
        
    def __str__(self):
        return self.name
    
    @staticmethod
    def post_payload():
        return {
            "name":  "Activity", 
            "description": "Example of activity for testing",
            "multiplier": 2, 
        }
        
    

class AdditiveRisks(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'additive_risks'
        
    def __str__(self):
        return self.name
        
    @staticmethod
    def post_payload():
        return {
            "name":  "Additive risk for testing", 
        }

class WeightWishes(models.Model):
    name = models.TextField()

    class Meta:
        managed = True
        db_table = 'weight_wishes'
        
    def __str__(self):
        return self.name

    @staticmethod
    def post_payload():
        return {
            "name":  "Weight wish for testing", 
        }

class Additives(models.Model):
    name = models.TextField()
    description = models.TextField()
    additive_risks = models.ForeignKey(AdditiveRisks, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'additives'
        
    def __str__(self):
        return self.name
        
    def fullname(self):
        return f"{self.name}: {self.description}"
        
        
    @staticmethod
    def post_payload():
        return {
            "name":  "Additive for testing", 
            "description":  "Description of an additive for testing", 
            'additive_risks': 'http://testserver/api/additive_risks/2/', 
        }
    
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
    history = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'biometrics'

    def __str__(self):
        return str(self.datetime)
        
                
    @staticmethod
    def post_payload():
        return {
            "datetime": '2023-06-11T05:35:13.673203Z', 
            "weight": 71.12, 
            "height":177, 
            "activities":'http://testserver/api/activities/2/', 
            "weight_wishes":  "http://testserver/api/weight_wishes/2/", 
        }
    
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
        
    def __str__(self):
        return self.name
    @staticmethod
    def post_payload():
        return {
            "name":  "Food type for testing", 
        }

class SystemCompanies(models.Model):
    name = models.TextField()
    last = models.DateTimeField()
    obsolete = models.BooleanField()

    class Meta:
        managed = True
        db_table = 'system_companies'
        
    def __str__(self):
        return self.name
        
        
    @staticmethod
    def post_payload():
        return {
            "name":  "System company for testing", 
            "last": '2023-06-11T05:35:13.673203Z', 
            "obsolete": False, 
        }
                
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
                        
    @staticmethod
    def post_payload(system_companies=False):
        system_companies_value= None if system_companies is False else "http://testserver/api/system_companies/2/"
        return {
            "last": '2023-06-11T05:35:13.673203Z', 
            "name": "Company for testing", 
            "obsolete": False, 
            "system_companies": system_companies_value, 
        }

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

    def __str__(self):
        return self.name

    @staticmethod
    def post_payload():
        return {
            "name":  "Format for testing", 
        }

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

    class Meta:
        managed = True
        db_table = 'system_products'

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
    def fullname_english(self):
        company=""
        if self.system_companies is not None:
            company=f" ({self.system_companies.name})"
        version_parent=""
        if self.version_parent is not None:
            version_parent=f" v{self.version.date()}"
        return f"{self.name}{company}{version_parent}"

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
    def post_payload():
            return {
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

    @staticmethod
    def hurl(request, id):
        return request.build_absolute_uri(reverse('products-detail', args=(id, )))
                
    @staticmethod
    def post_payload():
            return {
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
        
    def getUses(self):
        """
            Uses is an annotation in view set, so if I want to serialize an item I need to calculate them object by object
        """
        return Meals.objects.filter(products=self).count()+ ElaboratedProductsProductsInThrough.objects.filter(products=self).count() + ElaborationsProductsInThrough.objects.filter(products=self).count()

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
        
    @staticmethod
    def hurl(request, id):
        return request.build_absolute_uri(reverse('elaboratedproducts-detail', args=(id, )))

    @staticmethod
    def post_payload(recipes=None):
        return {
            "name": "Elaborated product for testing", 
            "final_amount": 1200, 
            "last": '2023-06-11T05:35:13.673203Z', 
            "food_types":'http://testserver/api/food_types/2/', 
            "obsolete": False, 
            "recipes":recipes, 
        }
    def is_deletable(self):
        if self.uses() >0:
            return False
        return True
        
    def get_products_in(self):
        if not hasattr(self, "_products_in") :
            self._products_in=ElaboratedProductsProductsInThrough.objects.select_related("products").prefetch_related("products__additives__additive_risks").filter(elaborated_products=self)
        return self._products_in


    def is_glutenfree(self):
        for pi_ in self.get_products_in():
            if pi_.products.glutenfree is False:
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
        for pi_ in self.get_products_in():
            pi_product_amount=pi_.products.amount
            pi_product_component=getattr(pi_.products, name)
            if pi_product_component is None or pi_product_amount==0:
                return None
            all_pi_component=all_pi_component+ pi_.amount*pi_product_component/pi_product_amount
            
        if total is True:
            return all_pi_component
        else:
            return 100*all_pi_component/self.final_amount     
            
    def additives_risk(self):
        r=0
        for pi_ in self.get_products_in():
            ar=pi_.products.additives_risk()
            if ar>r:
                r=ar
        return r

class ElaboratedProductsProductsInThrough(models.Model):
    products = models.ForeignKey(Products, on_delete=models.DO_NOTHING)
    elaborated_products = models.ForeignKey(ElaboratedProducts, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=3)

    @staticmethod
    def post_payload(products=None, elaborated_products=None):
        return {
            "products": products, 
            "amount": 1200, 
            "elaborated_products": elaborated_products
        }

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
        
    @staticmethod
    def post_payload(products):
        return {
            "datetime": '2023-06-11T05:35:13.673203Z', 
            "products": products, 
            "amount":  330, 
        }
        
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
    height = models.IntegerField( blank=False, null=False)#cm
    photo=models.ForeignKey(Files, on_delete=models.DO_NOTHING, blank=True, null=True) 

    class Meta:
        managed = True
        db_table = 'pots'

    def __str__(self):
        self.fullname()
        
    @staticmethod
    def post_payload():
        return {
            "name": 'Pot for testing', 
            "weight": 2000,
           "diameter": 20,  
            "height":  33, 
        }
    def fullname(self):
        return f"{self.name} ({self.diameter}cm, {self.weight}g)"
        
    def volume(self):
        return pi*pow(self.diameter/2, 2)*self.height

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
    @staticmethod
    def post_payload():
        return {
            "name":  "Recipe category type for testing", 
        }

class Recipes(models.Model):
    name = models.TextField()
    datetime=models.DateTimeField(blank=True, null=True)
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
        
        
    @staticmethod
    def post_payload():
        return {
            "name": 'Recipe for testing', 
            "datetime": '2023-06-11T05:35:13.673203Z', 
            "last": '2023-06-11T05:35:13.673203Z', 
            "food_types":'http://testserver/api/food_types/2/', 
            "obsolete":False, 
            "comment": "This is my recipe comment for testing", 
            "valoration": 20,  
            "guests":  True,
            "soon": True,  
            "recipes_categories": [], 
        }

    ##Returns a files url, then you can use content/ or thumbnail/
    def main_image_files(self, request):
        for rl in self.recipes_links.all().select_related("type", "files").values("files__id", "type__id"):
            if rl["type__id"]==eRecipeLink.MainPhoto:
                return request.build_absolute_uri(reverse('files-detail', args=(rl["files__id"], )))

        return None    
    
class RecipesLinksTypes(models.Model):
    name=models.TextField( blank=False, null=False)
    class Meta:
        managed = True
        db_table = 'recipes_links_types'
        
    def __str__(self):
        return self.name
    @staticmethod
    def post_payload():
        return {
            "name":  "Recipe link type for testing", 
        }
class RecipesLinks(models.Model):
    description=models.TextField( blank=False, null=False)
    type=models.ForeignKey(RecipesLinksTypes, models.DO_NOTHING)
    link=models.TextField( blank=False, null=True)
    files=models.ForeignKey(Files, on_delete=models.DO_NOTHING, blank=True, null=True) 
    recipes=models.ForeignKey(Recipes, related_name="recipes_links", on_delete=models.DO_NOTHING) 
    class Meta:
        managed = True
        db_table = 'recipes_links'
    @staticmethod
    def post_payload(recipes):
        return {
            "description":  "Recipe links for testing", 
            "type": 'http://testserver/api/recipes_links_types/3/',
           "link": "Link for testing", 
           "recipes":recipes, 
        }
    
    
class Elaborations(models.Model):
    diners = models.IntegerField( blank=False, null=False)
    elaborations_products_in = models.ManyToManyField(Products, through='ElaborationsProductsInThrough', blank=True)
    recipes=models.ForeignKey(Recipes, related_name="elaborations", on_delete=models.DO_NOTHING) 
    final_amount = models.DecimalField(max_digits=10, decimal_places=3, blank=True, null=True)
    automatic=models.BooleanField(blank=False, null=False, default=False)
    automatic_adaptation_step=models.TextField(blank=True, null=True)
    
    class Meta:
        managed = True
        db_table = 'elaborations'
        
    def __str__(self):
        return self.fullname()
    @staticmethod
    def post_payload(recipes):
        return {
            "diners": 4, 
            "recipes":  recipes, 
            "final_amount": 1000, 
            "automatic": False, 
            "automatic_adaptation_step": ""
        }
        
    def fullname(self):
        return _("{0} ({1} diners)").format(self.recipes.name, self.diners)
        
        
class ElaborationsTexts(models.Model):
    elaborations = models.OneToOneField("Elaborations", on_delete=models.CASCADE, primary_key=True , related_name="elaborations_texts")
    text=models.TextField( blank=True, null=False, db_comment="Recipe text for this elaboration in markdown format", default="")
    class Meta:
        managed = True
        db_table = 'elaborations_texts'
        
                    
    @staticmethod
    def get_ingredients_spans(htmlcode ):
        """
            Returns a list of string with ingredients spans 
        """
        r= findall(r'<span data-type="mention" class="mention_ingredients"(.*?)<\/span>', htmlcode)
        return r

    @staticmethod
    def get_containers_spans(htmlcode ):
        """
            Returns a list of string with containers spans 
        """
        r= findall(r'/<span data-type="MentionContainers" class="mention_containers"(.*?)<\/span>/g', htmlcode)
        return r
    
    @staticmethod
    def get_id_label_from_span(span):
        return {
            "id": span.split('data-id="')[1].split('" data-label')[0],
            "label": span.split('data-label="')[1].split('">')[0],
        }

    @staticmethod
    def span_ingredient(id,label):
        """
           Returns a string with the span container
        """
        return f"""<span data-type="mention" class="mention_ingredients" data-id="{id}" data-label="{label}">@{label}</span>"""

    @staticmethod
    def span_container(id,label):
        """
           Returns a string with the span container
        """
        return f"""<span data-type="MentionContainers" class="mention_containers" data-id="{id}" data-label="{label}">#{label}</span>"""

    @staticmethod
    def generate_automatic_text(new_automatic_elaboration, oldtext):
        """
            Returns a string with the newtext after updating spans in oldtext
        """
        qs_newpi=ElaborationsProductsInThrough.objects.filter(elaborations=new_automatic_elaboration)
        d_newpi_parents_id=commons.qs_dict(qs_newpi, lambda o: str(o.automatic_parent.id))
        
        #Ingredients
        ingredient_spans=ElaborationsTexts.get_ingredients_spans(oldtext)
        for span in ingredient_spans:
            id_label=ElaborationsTexts.get_id_label_from_span(span)
            oldspan=ElaborationsTexts.span_ingredient(id_label["id"], id_label["label"])
            newpi=d_newpi_parents_id[id_label["id"]]
            newspan=ElaborationsTexts.span_ingredient(newpi.id, newpi.fullname())
            oldtext=oldtext.replace(oldspan,newspan )

        return oldtext
        
        
class MeasuresTypes(models.Model):
    name=models.TextField( blank=False, null=False)
    class Meta:
        managed = True
        db_table = 'measures_types'
        
    def __str__(self):
        return self.name

    def localname(self):
        return _(self.name)
    @staticmethod
    def post_payload():
        return {
            "name":  "Measure type for testing", 
        }

class ElaborationsProductsInThrough(models.Model):
    products = models.ForeignKey(Products, on_delete=models.DO_NOTHING)
    elaborations = models.ForeignKey(Elaborations, on_delete=models.DO_NOTHING)
    measures_types = models.ForeignKey(MeasuresTypes, on_delete=models.DO_NOTHING)
    amount = models.DecimalField(max_digits=10, decimal_places=3)
    comment = models.CharField(max_length=100, blank=True, null=True) #Add product aclarations, cut, temperature...
    ni=models.BooleanField(blank=False, null=False, default=True) #Must be used for nutritional information calcs
    automatic_percentage=models.IntegerField(null=False, blank=False, default=100 )#Percentage 0-100 to scale in automatic elaborations
    automatic_parent=models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True, db_comment="Parent ElaborationProductsIn for this register", default=None)
 
    @staticmethod
    def post_payload(elaborations, products):
        return {
            "elaborations": elaborations, 
            "products": products, 
            "measures_types":  'http://testserver/api/measures_types/2/', 
            "amount": 1212, 
            "comment": "Elaboration comment for testing", 
            "ni": True, 
            "automatic_percentage": 100, 
        }

    def final_grams(self):
        if self.ni is False:
            return 0
        if self.measures_types.id==1:#Grams
            return self.amount
        elif self.measures_types.id==2:#Milliliters
            return self.amount if self.products.density is None else self.products.density*self.amount
        elif self.measures_types.id==3:#Table spoon
            return self.amount*15 if self.products.density is None else self.products.density*self.amount*15
        elif self.measures_types.id==4:#Tee spoon
            return self.amount*5 if self.products.density is None else self.products.density*self.amount*5
        elif self.measures_types.id==5:#Cup
            return self.amount*240 if self.products.density is None else self.products.density*self.amount*240

    def fullname(self):
        comment_string="" if self.comment is None or self.comment=="" else f" ({self.comment})"
        if self.measures_types.id==1:#Grams
            return _("{0} g of {1}{2}").format(round(self.amount, 1), _(self.products.name), comment_string)
        if self.measures_types.id==2:#Milliliters
            return _("{0} ml of {1}{2}").format(round(self.amount, 1), _(self.products.name), comment_string)
        else:
            return _("{0} {1} of {2}{3}").format(Fraction(self.amount), _(self.measures_types.localname()).lower(), _(self.products.name), comment_string)


class ElaborationsContainers(models.Model):
    name=models.TextField( blank=False, null=False)
    elaborations = models.ForeignKey(Elaborations, related_name="elaborations_containers", on_delete=models.CASCADE)
    
    class Meta:
        managed = True
        db_table = 'elaborations_containers'

    def __str__(self):
        return self.name

    @staticmethod
    def post_payload(elaborations):
        return {
            "name":  "Elaboration container for testing", 
            "elaborations": elaborations
        }

class ElaborationsExperiences(models.Model):
    datetime = models.DateTimeField(blank=False, null=False)
    experience=models.TextField( blank=False, null=False)
    elaborations = models.ForeignKey(Elaborations, related_name="elaborations_experiences", on_delete=models.CASCADE)
    
    class Meta:
        managed = True
        db_table = 'elaborations_experiences'

    def __str__(self):
        return self.name

    @staticmethod
    def post_payload(elaborations):
        return {
            "datetime": '2023-06-11T05:35:13.673203Z', 
            "experience":  "Elaboration experience for testing", 
            "elaborations": elaborations
        }

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

class eRecipeLink:
    MainPhoto=7


def time_to_timedelta(time):
    d=datetime(2022, 12, 1, 0, 0, 0, 0)
    return datetime.combine(d.date(), time)-d
    
def get_or_None(model, id):
    try:
        return model.objects.get(pk=id)
    except:
        return None


def timedelta_to_string(td):
        s=td.total_seconds()
        
        dias=int(s/(24*60*60))
        segundosquedan=fmod(s,24*60*60)
        horas=int(segundosquedan/(60*60))
        segundosquedan=fmod(segundosquedan,60*60)
        minutos=int(segundosquedan/60)
        segundosquedan=fmod(segundosquedan,60)
        segundos=int(segundosquedan)
        r=""
        if dias>0:
            r=r+_("{0} days ").format(dias)
        if horas>0:
            r=r+_("{0} hours ").format(horas)
        if minutos>0:
            r=r+_("{0} minutes ").format(minutos)
        if segundos>0:
            r=r+_("{0} seconds ").format(segundos)
            
        return r[:-1]
