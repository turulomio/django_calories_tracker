from calories_tracker import models
from . import tests_helpers


def test_activities(self):
    tests_helpers.common_tests_PrivateEditableCatalog(self, '/api/activities/', models.Activities.post_payload(),
                                                        self.client_authorized_1, self.client_anonymous,
                                                        self.client_catalog_manager)