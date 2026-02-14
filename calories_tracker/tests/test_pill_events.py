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
    
def test_copy_last_week(self):    
    dt_base = timezone.now().replace(microsecond=0)
    # Create 2 events in the previous 7 days
    models.PillEvents.objects.create(user=self.user_authorized_1, pillname="Pill A", dt=dt_base - timedelta(days=3), highlight_late=True)
    models.PillEvents.objects.create(user=self.user_authorized_1, pillname="Pill B", dt=dt_base - timedelta(days=5), highlight_late=False)
    
    # Call action with explicit dt_from
    response_data = tests_helpers.client_post(self, self.client_authorized_1, '/api/pill_events/copy_last_week/', {"dt_from": dt_base}, status.HTTP_200_OK)
    self.assertEqual(len(response_data), 2)
    
    # Verify the new events in DB
    new_events = models.PillEvents.objects.filter(user=self.user_authorized_1, dt__gte=dt_base)
    self.assertEqual(new_events.count(), 2)
    
    event_a = new_events.get(pillname="Pill A")
    self.assertEqual(event_a.dt, dt_base + timedelta(days=4)) # (base - 3) + 7 = base + 4
    self.assertTrue(event_a.highlight_late)
    self.assertIsNone(event_a.dt_intake)

    # Test without dt_from (defaults to now)
    tests_helpers.client_post(self, self.client_authorized_1, '/api/pill_events/copy_last_week/', {}, status.HTTP_200_OK)