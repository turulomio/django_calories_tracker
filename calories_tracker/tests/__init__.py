from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from calories_tracker.tests.tests_dinamic_methods import add_method_to_this_class_dinamically

class CaloriesTrackerAPITestCase(APITestCase):
    """
    Base class for API tests.
    It sets up fixtures and authenticated clients once for all inheriting test classes.
    """
    fixtures = ["all.json","test_users.json"]
    _setup_done = False

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs )   
        # add_methodtypes_to_this_object_dinamically(self)

    @classmethod
    def setUpClass(cls):
        """
        Set up non-database specific resources once for all test classes.
        """
        super().setUpClass()

        if CaloriesTrackerAPITestCase._setup_done:
            return

        CaloriesTrackerAPITestCase.user_authorized_1 = User.objects.get(username='authorized_1')
        CaloriesTrackerAPITestCase.user_authorized_2 = User.objects.get(username='authorized_2')
        CaloriesTrackerAPITestCase.user_catalog_manager = User.objects.get(username='catalog_manager')

        CaloriesTrackerAPITestCase.client_authorized_1 = APIClient()
        CaloriesTrackerAPITestCase.client_authorized_1.force_authenticate(user=CaloriesTrackerAPITestCase.user_authorized_1)
        CaloriesTrackerAPITestCase.client_authorized_1.user = CaloriesTrackerAPITestCase.user_authorized_1

        CaloriesTrackerAPITestCase.client_authorized_2 = APIClient()
        CaloriesTrackerAPITestCase.client_authorized_2.force_authenticate(user=CaloriesTrackerAPITestCase.user_authorized_2)
        CaloriesTrackerAPITestCase.client_authorized_2.user = CaloriesTrackerAPITestCase.user_authorized_2

        CaloriesTrackerAPITestCase.client_anonymous = APIClient()
        CaloriesTrackerAPITestCase.client_anonymous.user = None

        CaloriesTrackerAPITestCase.client_catalog_manager = APIClient()
        CaloriesTrackerAPITestCase.client_catalog_manager.force_authenticate(user=CaloriesTrackerAPITestCase.user_catalog_manager)
        CaloriesTrackerAPITestCase.client_catalog_manager.user = CaloriesTrackerAPITestCase.user_catalog_manager

        CaloriesTrackerAPITestCase._setup_done = True
        print("LOADED SETUPCLASS")
add_method_to_this_class_dinamically(CaloriesTrackerAPITestCase, "calories_tracker/tests", "test_*.py")
