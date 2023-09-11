from base64 import b64encode
from calories_tracker.reusing.responses_json import json_data_response
from calories_tracker import __version__
from datetime import datetime
from django.conf import settings
from django.utils.translation import gettext as _
from mimetypes import guess_type
from os import path
from unogenerator import ODT

def response_report_elaboration(request, elaboration):
    template=f"{path.dirname(__file__)}/templates/ReportElaboration.odt"
    diners=_("{0} diners").format(elaboration.diners)
    filename=f'{settings.TMPDIR_REPORTS}/CT. {elaboration.recipes.name}. {diners}.pdf'
    with ODT(template) as doc:

        doc.setMetadata( 
            _("Recipe elaboration"),  
            _("This is an automatic generated report from Calories Tracker"), 
            "Turulomio", 
            "CaloriesTracker-{}".format(__version__)
        )
        
        doc.find_and_replace("__TITLE__", elaboration.recipes.name)
        doc.find_and_replace("__DATETIME__", str(elaboration.recipes.last.date()))
        
        doc.find_and_replace("__CONTENT__", "")
        doc.addParagraph(_("Ingredients for {0} diners").format(elaboration.diners), "Heading 1")
        for ingredient in elaboration.elaborationsproductsinthrough_set.all().order_by("-amount").select_related("products", "measures_types"):
            doc.addParagraph(ingredient.fullname(), "Ingredients")
            
        doc.addParagraph(_("Containers"), "Heading 1")
        for c in elaboration.elaborations_containers.all().order_by("name"):
            doc.addParagraph(c.name, "ElaborationsContainers")
            
        if hasattr(elaboration,  "elaborations_texts"):
            doc.addParagraph(_("Recipe"), "Heading 1")
            doc.addHTMLBlock(elaboration.elaborations_texts.text)

            
        doc.addParagraph("", "Standard")
        doc.find_and_delete_until_the_end_of_document('Styles to remove')    
        
        # Document Generation
        doc.export_pdf(filename)
    return json_response_file(filename)
    
def response_report_shopping_list(request, elaborations):
    template=f"{path.dirname(__file__)}/templates/ReportElaboration.odt"
    filename=f'{settings.TMPDIR_REPORTS}/ShoppingList.pdf'
    with ODT(template) as doc:
        doc.setMetadata( 
            _("Shopping list"),  
            _("This is an automatic generated report from Calories Tracker"), 
            "Turulomio", 
            "CaloriesTracker-{}".format(__version__)
        )
        
        doc.find_and_replace("__TITLE__", _("Shopping list"))
        doc.find_and_replace("__DATETIME__", str(datetime.now()))
        doc.find_and_replace("__CONTENT__", "")
        
        doc.addParagraph(_("Recipes"), "Heading 1")
        for e in elaborations:
            doc.addParagraph(e.fullname(), "ElaborationsContainers")
            
        ## Generate a dictionary with p as key
        list={}
        for e in elaborations:
            for i in e.elaborationsproductsinthrough_set.all().select_related("products__companies", "measures_types"):
                if not i.products in list:
                    list[i.products]=0
                list[i.products]=list[i.products]+i.final_grams()

        doc.addParagraph(_("Shopping list"), "Heading 1")
        for k, v in list.items():            
            doc.addParagraph(f"{int(v)}g\t{k.fullname()}", "ElaborationsContainers")
            
        doc.addParagraph("", "Standard")
        doc.find_and_delete_until_the_end_of_document('Styles to remove')    
        doc.export_pdf(filename)
    return json_response_file(filename)
    
def dict_response_file(filename):
    with open(filename, "rb") as pdf:
        encoded_string = b64encode(pdf.read())
        r={"filename":path.basename(filename),  "mime": guess_type(filename)[0],  "data":encoded_string.decode("UTF-8")}
    return r

def json_response_file(filename):
        return json_data_response( True, dict_response_file(filename),  _("OK"))
