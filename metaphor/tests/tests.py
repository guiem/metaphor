from django.test import TestCase
from metaphor.utils import get_random_connectors, CONNECTORS

class UtilsTest(TestCase):

    def create_whatever(self, title="only a test", body="yes, this is only a test"):
        return Whatever.objects.create(title=title, body=body, created_at=timezone.now())

    def test_get_random_connectors(self):
        num_connectors = 5
        connectors = get_random_connectors(num_connectors)
        self.assertEqual(len(connectors),num_connectors)
        for con in connectors:
            self.assertIn(con,CONNECTORS)
        