from calories_tracker.tests_helpers import TestModel, td_string, td_timezone, td_integer, td_decimal

    
class tmActivities(TestModel):
    catalog=True
    private=False
    examples=[
        {
            "name":td_string(), 
            "description": td_string(), 
            "multiplier": td_decimal(), 
        }, 
    ]
    
    
class tmAdditiveRisks(TestModel):
    catalog=True
    private=False

class tmAdditives(TestModel):
    catalog=True
    private=False
    examples=[
        {
            "name":td_string(), 
            "description": td_string(), 
            "additive_risks":[tmAdditiveRisks.hlu(1)], 
        }, 
    ]
    
class tmWeightWishes(TestModel):
    catalog=True
    private=False
    
class tmBiometrics(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "datetime": td_timezone(), 
            "weight": td_integer(), 
            "height": td_integer(), 
            "activities": tmActivities.hlu(0), 
            "weight_wishes": tmWeightWishes.hlu(0), 
        }
    ]
    
class tmCompanies(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "name": "My company", 
            "obsolete":False, 
        }
    ]
    
class tmFoodTypes(TestModel):
    catalog=True
    private=False
    
class tmElaboratedProducts(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "name": "My elaborated product", 
            "final_amount":1111, 
            "food_types": tmFoodTypes.hlu(1), 
            "obsolete": False, 
            "products_in": []
        }
    ]
        
class tmRecipes(TestModel):
    catalog=False
    private=True
    examples=[
        {
                "datetime": td_timezone(), 
                "name": "My recipe", 
                "final_amount":1111, 
                "food_types": tmFoodTypes.hlu(1), 
                "obsolete": False, 
                "comment": td_string(),
                "valoration": 99,
                "guests": True, 
                "soon": True, 
                "recipes_categories":[], 
                
        }
    ]        
    
    
class tmRecipesLinksTypes(TestModel):
    catalog=True
    private=False
    
    examples=[
        {
            "name":td_string(), 
        }, 
    ]
    
class tmRecipesLinks(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "description": "My recipe link", 
            "type": tmRecipesLinksTypes.hlu(1) , 
            "recipes": tmRecipes, 
            "content": "", 
            "link": td_string(), 
            "mime":"image/png"
        }
    ]
        
class tmElaborations(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "diners": 4, 
            "final_amount":1111, 
            "recipes": tmRecipes,
            "elaborations_products_in":[], 
            "automatic":False, 
        }
    ]        

class tmElaborationsContainers(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "name": td_string(), 
            "elaborations":tmElaborations, 
        }
    ]
    
class tmElaborationsExperiences(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "datetime":td_timezone(), 
            "experience": td_string(), 
            "elaborations":tmElaborations, 
        }
    ]

class tmSteps(TestModel):
    catalog=True
    private=False
    
class tmElaborationsSteps(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "duration": "00:01:00", 
            "order": 1, 
            "elaborations": tmElaborations,
            "steps": tmSteps.hlu(2),
        }
    ]
        
class tmPots(TestModel):
    catalog=False
    private=True
    examples=[
        {
                    "name": "My Pot", 
                    "diameter": 1, 
                    "weight": 1, 
                    "height": 1, 
        }
    ]
    
    
class tmStirTypes(TestModel):
    catalog=True
    private=False
class tmSystemCompanies(TestModel):
    catalog=True
    private=False
class tmSystemProducts(TestModel):
    catalog=True
    private=False
class tmTemperaturesTypes(TestModel):
    catalog=True
    private=False

class tmMeasuresTypes(TestModel):
    catalog=True
    private=False

class tmRecipesCategories(TestModel):
    catalog=True
    private=False

    
class tmProducts(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "calories": td_decimal(), 
            "food_types": tmFoodTypes.hlu(1), 
            "name": td_string(), 
            "amount": td_decimal(), 
            "formats":[], 
            "glutenfree":True, 
            "obsolete":False, 
        }
    ]    
class tmMeals(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "datetime": td_timezone(), 
            "products": tmProducts, 
            "amount": 1, 
        }
    ]
    
class tmElaborationsProductsInThrough(TestModel):
    catalog=False
    private=True
    examples=[
        {
            "products": tmProducts, 
            "amount": 1, 
            "measures_types": tmMeasuresTypes.hlu(1), 
            "elaborations": tmElaborations, 
        }
    ]
    
    @classmethod
    def url_model_name(cls):
        return "elaborationsproductsinthrough"
    
