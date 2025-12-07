from calories_tracker import models
from . import tests_helpers, CaloriesTrackerAPITestCase
from datetime import date, timedelta
from django.test import tag
from django.utils import timezone
from json import loads
from pydicts import lod
from rest_framework import status


tag, models

    
def test_pill_events(self):
    # Common vars
    pillname="Pill name"
    dt_from=timezone.now()
    days=5
    #LIST NOT STANDARD tests_helpers.common_tests_Private(self,  '/api/pill_events/', models.PillEvents.post_payload(),  self.client_authorized_1, self.client_authorized_2, self.client_anonymous)
    
    # Removes pillevents from dt. Round timezones use 1 second minus
    #deleted=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/delete_from_dt/',  {"pillname": "Pill name",  "dt_from": timezone.now()-timedelta(hours=1)},  status.HTTP_200_OK)        

    # POST
    tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/', models.PillEvents.post_payload(), status.HTTP_201_CREATED)

    # LIST
    tests_helpers.client_get(self, self.client_authorized_1, '/api/pill_events/', status.HTTP_400_BAD_REQUEST)
    lod_pe=tests_helpers.client_get(self, self.client_authorized_1, f'/api/pill_events/?year={dt_from.year}&month={dt_from.month}', status.HTTP_200_OK)
    self.assertEqual(len(lod_pe), 1)
    # DELETE
    tests_helpers.client_delete(self, self.client_authorized_1, lod_pe[0]["url"], {}, status.HTTP_204_NO_CONTENT)


    
    # Set pillevents each dt
    lod_pe=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/set_each_day/',  {"pillname": pillname,  "dt_from": dt_from, "days": days},  status.HTTP_200_OK)
    self.assertEqual(len(lod_pe), 5)

    deleted=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/delete_from_dt/',  {"pillname": pillname,  "dt_from": dt_from-timedelta(seconds=1)},  status.HTTP_200_OK)        
    self.assertEqual(deleted[0], 5)
    
    # Each n hours
    lod_pe=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/set_each_n_hours/',  {"pillname": pillname,  "dt_from": dt_from, "hours": 8,  "number":9},  status.HTTP_200_OK)
    self.assertEqual(len(lod_pe), 9)
    deleted=tests_helpers.client_post(self, self.client_authorized_1,  '/api/pill_events/delete_from_dt/',  {"pillname": pillname,  "dt_from": dt_from-timedelta(seconds=1)},  status.HTTP_200_OK)        
    self.assertEqual(deleted[0], 9)
    