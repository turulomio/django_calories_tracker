from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

def test_elaborated_products(self):
    # Due to elaborated_products DELETE is not standard due to it doesn't return HTTP_204_NOT_CONTENT y RuntimeError
    # common_tests_PrivateCatalog code manually
    # START OF COPIED METHOD
    ### TEST OF CLIENT_AUTHENTICATED_1
    apitestclass=self
    client_authenticated_1=self.client_authorized_1
    client_authenticated_2=self.client_authorized_2
    client_anonymous=self.client_anonymous
    post_url="/api/elaborated_products/"
    post_payload=models.ElaboratedProducts.post_payload()
    ### ALWAYS ONE REGISTER TO TEST FALBACK ID
    dict_post=tests_helpers.client_post(apitestclass, client_authenticated_1, post_url, post_payload, status.HTTP_201_CREATED)
    
    ### TEST OF CLIENT_AUTHENTICATED_1
    tests_helpers.common_actions_tests(apitestclass, client_authenticated_1, post_url, post_payload, dict_post["id"], 
        post=status.HTTP_201_CREATED, 
        get=status.HTTP_200_OK, 
        list=status.HTTP_200_OK, 
        put=status.HTTP_200_OK, 
        patch=status.HTTP_200_OK, 
        delete=status.HTTP_200_OK
    )

    # 1 creates and 2 cant get
    r1=client_authenticated_1.post(post_url, post_payload, format="json")
    apitestclass.assertEqual(r1.status_code, status.HTTP_201_CREATED, f"{post_url}, {r1.content}")
    r1_id=loads(r1.content)["id"]

    hlu_id_r1=tests_helpers.hlu(post_url,r1_id)
    
    r=client_authenticated_2.get(hlu_id_r1)
    apitestclass.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND, f"{post_url}, {r.content}. Client2 can access Client1 post")

    ### TEST OF CLIENT_ANONYMOUS
    tests_helpers.common_actions_tests(apitestclass, client_anonymous, post_url, post_payload, dict_post["id"], 
        post=status.HTTP_401_UNAUTHORIZED, 
        get=status.HTTP_401_UNAUTHORIZED, 
        list=status.HTTP_401_UNAUTHORIZED, 
        put=status.HTTP_401_UNAUTHORIZED, 
        patch=status.HTTP_401_UNAUTHORIZED, 
        delete=status.HTTP_401_UNAUTHORIZED
    )     

    # END OF COPIED METHOD
