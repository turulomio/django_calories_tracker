from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

def test_biometrics(self):
    tests_helpers.common_tests_Private(self,  '/api/biometrics/', models.Biometrics.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
    #Today
    tests_helpers.client_get(self, self.client_authorized_1, f'/api/biometrics/?day={date.today()}', status.HTTP_200_OK)
    #Empty day
    tests_helpers.client_get(self, self.client_authorized_1, '/api/biometrics/?day=2022-01-01', status.HTTP_200_OK)
