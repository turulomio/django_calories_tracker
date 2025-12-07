from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models


def test_weight_wishes(self):
    tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/weight_wishes/', models.WeightWishes.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
    