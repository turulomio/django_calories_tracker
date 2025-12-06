from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from calories_tracker.tests.tests_dinamic_methods import add_method_to_this_class_dinamically

class CaloriesTrackerAPITestCase(APITestCase):
    """
    Base class for API tests.
    It sets up fixtures and authenticated clients once for all inheriting test classes.
    """
    fixtures = ["all.json","test_users.json"]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs )   
        # add_methodtypes_to_this_object_dinamically(self)

    @classmethod
    def setUpClass(cls):
        """
        Set up non-database specific resources once for all test classes.
        """
        super().setUpClass()


        cls.user_authorized_1 = User.objects.get(username='authorized_1')
        cls.user_authorized_2 = User.objects.get(username='authorized_2')
        cls.user_catalog_manager = User.objects.get(username='catalog_manager')

        cls.client_authorized_1 = APIClient()
        cls.client_authorized_1.force_authenticate(user=cls.user_authorized_1)
        cls.client_authorized_1.user = cls.user_authorized_1

        cls.client_authorized_2 = APIClient()
        cls.client_authorized_2.force_authenticate(user=cls.user_authorized_2)
        cls.client_authorized_2.user = cls.user_authorized_2

        cls.client_anonymous = APIClient()
        cls.client_anonymous.user = None

        cls.client_catalog_manager = APIClient()
        cls.client_catalog_manager.force_authenticate(user=cls.user_catalog_manager)
        cls.client_catalog_manager.user = cls.user_catalog_manager


add_method_to_this_class_dinamically(CaloriesTrackerAPITestCase, "calories_tracker/tests", "test_*.py")
