from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models


def test_statistics(self):
    tests_helpers.client_get(self, self.client_authorized_1, "/statistics/", status.HTTP_200_OK)
