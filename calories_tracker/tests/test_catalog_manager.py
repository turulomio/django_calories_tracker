from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

def test_catalog_manager(self):
    r=tests_helpers.client_get(self, self.client_authorized_1, '/catalog_manager/', status.HTTP_200_OK)
    self.assertEqual(r, False)
    r=tests_helpers.client_get(self, self.client_catalog_manager, '/catalog_manager/', status.HTTP_200_OK)
    self.assertEqual(r, True)

