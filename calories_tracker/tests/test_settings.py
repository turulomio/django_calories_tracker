from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models
def test_settings(self):
    #Get
    tests_helpers.client_get(self, self.client_authorized_1, "/settings/", status.HTTP_200_OK)
    #Bad post
    tests_helpers.client_post(self, self.client_authorized_1, "/settings/",  {}, status.HTTP_400_BAD_REQUEST)
    #Good post
    tests_helpers.client_post(self, self.client_authorized_1, "/settings/",  {'first_name': 'Testing', 'last_name': 'Testing', 'last_login': '2023-06-13T07:05:01.293Z', 'email': 'testing@testing.com', 'birthday': '2000-01-01', 'male': True}, status.HTTP_200_OK)
    #Get again
    tests_helpers.client_get(self, self.client_authorized_1, "/settings/", status.HTTP_200_OK)
