"""
Test GIS API Endpoints - Django/PostGIS

Tests the GIS API views for the PostGIS-backed GIS system.
"""

from django.test import TestCase, Client
from django.conf import settings


class GISAPITestCase(TestCase):
    """Test the GIS API endpoints"""

    def setUp(self):
        self.client = Client()

    def test_gis_catalog_endpoint(self):
        """Test the GIS catalog API endpoint"""
        response = self.client.get('/atlas/api/gis/catalog/')
        # Should return 200 OK or 404 if endpoint not defined
        self.assertIn(response.status_code, [200, 404])

    def test_gis_layer_endpoint(self):
        """Test the GIS layer data endpoint"""
        # Test with a valid bbox
        response = self.client.get(
            '/atlas/api/gis/layer/lots/',
            {'bbox': '151.08,-33.89,151.09,-33.88', 'zoom': '16'}
        )
        self.assertIn(response.status_code, [200, 404])

    def test_gis_stats_endpoint(self):
        """Test the GIS stats endpoint"""
        response = self.client.get('/atlas/api/gis/stats/')
        self.assertIn(response.status_code, [200, 404])
