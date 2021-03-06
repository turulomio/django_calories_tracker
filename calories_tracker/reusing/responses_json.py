## THIS IS FILE IS FROM https://github.com/turulomio/reusingcode/python/responses_json.py
## IF YOU NEED TO UPDATE IT PLEASE MAKE A PULL REQUEST IN THAT PROJECT AND DOWNLOAD FROM IT
## DO NOT UPDATE IT IN YOUR CODE

from base64 import b64encode
from decimal import Decimal
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

class MyDjangoJSONEncoder(DjangoJSONEncoder):    
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, bytes):
            return b64encode(o).decode("UTF-8")
        return super().default(o)

def json_success_response(success, detail):
    """
        Returns a predefined json response
            - success: bool
            - detail: Description of success
    """
    if not success.__class__.__name__=="bool" or not detail.__class__.__name__=="str":
        print("json_succcess_response parameters are wrong")
        
    return JsonResponse( {"success": success, "detail": detail}, encoder=MyDjangoJSONEncoder, safe=True)
    
def json_data_response(success, data,  detail=""):
    """
        Returns a predefined json response
            - success: bool
            - data: Dict
            - detail: Description of success
    """
    if not success.__class__.__name__=="bool" or not detail.__class__.__name__=="str" or not data.__class__.__name__ in ["dict", "OrderedDict"]:
        print("json_succcess_response parameters are wrong")
        
    return JsonResponse( {"success": success,  "data": data,  "detail": detail}, encoder=MyDjangoJSONEncoder, safe=True)
