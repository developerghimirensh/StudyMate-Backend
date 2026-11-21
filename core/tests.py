from django.test import SimpleTestCase
from django.urls import resolve, Resolver404

class FeatureRouteTests(SimpleTestCase):
    def test_active_routes_are_mounted(self):
        paths = [
            '/api/v1/health/', '/api/v1/security/setup/', '/api/v1/subjects/',
            '/api/v1/tasks/', '/api/v1/decks/', '/api/v1/flashcards/',
            '/api/v1/progress/analytics/', '/api/v1/dashboard/',
        ]
        for route in paths:
            with self.subTest(route=route):
                self.assertIsNotNone(resolve(route))

    def test_upload_and_sync_routes_are_not_mounted(self):
        for route in ['/api/v1/materials/', '/api/v1/sync/push/']:
            with self.subTest(route=route):
                with self.assertRaises(Resolver404):
                    resolve(route)
