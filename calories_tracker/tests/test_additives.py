from calories_tracker import models
from . import tests_helpers


def test_additives(self):
    tests_helpers.common_tests_PrivateEditableCatalog(self,  '/api/additives/', models.Additives.post_payload(),  self.client_authorized_1, self.client_anonymous, self.client_catalog_manager)
        
