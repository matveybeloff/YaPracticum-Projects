from django.test import TestCase
from rest_framework.test import APIClient


class SmokeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_docs_schema_available(self):
        resp = self.client.get('/api/schema.json')
        self.assertIn(resp.status_code, (200, 301, 302))

    def test_users_list_open(self):
        resp = self.client.get('/api/users/')
        self.assertEqual(resp.status_code, 200)

    def test_tags_list_open(self):
        resp = self.client.get('/api/tags/')
        self.assertEqual(resp.status_code, 200)
