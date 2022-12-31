from django.core.management import call_command
from django.db import connection
from django.urls import reverse
from io import StringIO
from json import loads
from rest_framework import status
from tabulate import tabulate

#Hyperlinkurl
def hlu(name, id):
    return 'http://testserver' + reverse(name+'-detail', kwargs={'pk': id})

def call_command_sqlsequencerreset(appname):
    """
        Execute python manager sqlsequencereset
    """
    output=StringIO()
    call_command("sqlsequencereset", appname, stdout=output, no_color=True)
    sql = output.getvalue()
    with connection.cursor() as cursor:
        cursor.execute(sql)

def test_cross_user_data_with_post(apitestclass, client1,  client2,  post_url, dict_to_post):
    """
        Test to check if a recent post by client 1 is accessed by client2
        
        Returns the content of the post
        
        example:
        test_cross_user_data_with_post(self, client1, client2, "/api/biometrics/", { "datetime": timezone.now(), "weight": 71, "height": 180, "activities": hlu("activities", 0), "weight_wishes": hlu("weightwishes", 0)})
    """
    
    r=client1.post(post_url, dict_to_post, format="json")    
    apitestclass.assertEqual(r.status_code, status.HTTP_201_CREATED, f"{post_url}, {r.content}")
    return_=r.content
    testing_id=loads(r.content)["id"]
    
    #other tries to access url
    r=client1.get(f"{post_url}{testing_id}/")
    apitestclass.assertEqual(r.status_code, status.HTTP_200_OK,  f"{post_url}, {r.content}")
    
    #other tries to access url
    r=client2.get(f"{post_url}{testing_id}/")
    apitestclass.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND, f"{post_url}, {r.content}. WARNING: Client2 can access Client1 post")
    
    return loads(return_)
    
    

def test_cross_user_data(apitestclass, client1,  client2,  url):
    """
        Test to check if a hyperlinked model url can be accesed by client_belongs and not by client_other
        
        example:
        test_cross_user_data(self, client1, client2, "/api/biometrics/2/"})
    """
   
    #other tries to access url
    r=client1.get(url)
    apitestclass.assertEqual(r.status_code, status.HTTP_200_OK,  url)
    
    #other tries to access url
    r=client2.get(url)
    apitestclass.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND, f"{url}. WARNING: Client2 can access Client1 post")
    
#    
#def lod_to_headers_and_data(lod):
#    if len(lod)==0:
#        return None
#    
#    headers=lod[0].keys()
#    data=[]
#    for d in lod:
#        data_row=[]
#        for header in headers:
#            data_row.append(d[header])
#        data.append(data_row)
#    return headers, data
    
def print_list(client, list_url, limit=10):
    r=client.get(list_url)
    print(f"\nPrinting {limit} rows of {list_url}")
    lod=loads(r.content)[:limit]
    print(tabulate(lod, headers="keys", tablefmt="psql"))
        
