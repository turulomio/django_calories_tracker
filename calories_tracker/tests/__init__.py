from django.contrib.auth.models import User, Group
from rest_framework.test import APIClient, APITestCase


class CaloriesTrackerAPITestCase(APITestCase):
    """
    Base class for API tests.
    It sets up fixtures and authenticated clients once for all inheriting test classes.
    """
    fixtures = ["all.json"]

    _setup_done = False

    @classmethod
    def setUpClass(cls):
        """
        Set up data for all test classes.
        This method is run once for the first test class that inherits from it.
        """
        super().setUpClass()

        if cls._setup_done:
            return

        # User to test api
        cls.user_authorized_1 = User.objects.create_user(
            username='authorized_1',
            password='testing123',
            email='testing@testing.com',
            first_name='Testing',
            last_name='Testing',
        )

        # User to confront security
        cls.user_authorized_2 = User.objects.create_user(
            username='authorized_2',
            password='other123',
            email='other@other.com',
            first_name='Other',
            last_name='Other',
        )

        # User to test api
        cls.user_catalog_manager = User.objects.create_user(
            username='catalog_manager',
            password='catalog_manager123',
            email='catalog_manager@catalog_manager.com',
            first_name='Catalog',
            last_name='Manager',
        )
        cls.user_catalog_manager.groups.add(Group.objects.get(name='CatalogManager'))

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

        cls._setup_done = True
        print("LOADED")