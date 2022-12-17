from base64 import b64encode
from calories_tracker.reusing.responses_json import json_data_response
from calories_tracker import __version__
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
        for ingredient in elaboration.elaborationsproductsinthrough_set.all().order_by("-amount"):
            doc.addParagraph(ingredient.fullname(), "Ingredients")
            
        doc.addParagraph(_("Containers"), "Heading 1")
        for c in elaboration.elaborations_containers.all().order_by("name"):
            doc.addParagraph(c.name, "ElaborationsContainers")
            
        doc.addParagraph(_("Recipe steps"), "Heading 1")
        for es in elaboration.elaborations_steps.all().order_by("order"):
            doc.addParagraph(es.wording(), "ElaborationsSteps")
            
        doc.addParagraph("", "Standard")
        doc.find_and_delete_until_the_end_of_document('Styles to remove')    
        
        # Document Generation
        doc.export_pdf(filename)
    return json_response_file(filename)
    
def json_response_file(filename):
    with open(filename, "rb") as pdf:
        encoded_string = b64encode(pdf.read())
        r={"filename":path.basename(filename),  "mime": guess_type(filename)[0],  "data":encoded_string.decode("UTF-8")}
        return json_data_response( True, r,  _("OK"))
