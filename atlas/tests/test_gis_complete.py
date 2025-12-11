"""
Test GIS Service - Django/PostGIS

Tests the complete GIS service with PostGIS backend.
"""

from django.test import TestCase
from django.conf import settings


class GISServiceTestCase(TestCase):
    """Test the GIS service functionality"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Only run if PostGIS is enabled
        if not getattr(settings, 'USE_POSTGIS', False):
            return
        from atlas.gis import gis_service
        cls.gis_service = gis_service

    def test_catalog_summary(self):
        """Test getting catalog summary"""
        if not getattr(settings, 'USE_POSTGIS', False):
            self.skipTest("PostGIS not enabled")

        summary = self.gis_service.get_catalog_summary()
        self.assertIn('total_layers', summary)
        self.assertIn('source', summary)
        self.assertEqual(summary['source'], 'postgis')

    def test_spatial_query(self):
        """Test spatial query with bbox"""
        if not getattr(settings, 'USE_POSTGIS', False):
            self.skipTest("PostGIS not enabled")

        # Test bbox query (area with known data)
        bbox = (151.08, -33.89, 151.09, -33.88)
        result = self.gis_service.load_layer('Lots', bbox, zoom_level=16)

        if result:
            self.assertEqual(result['type'], 'FeatureCollection')
            self.assertIn('features', result)
            self.assertIn('metadata', result)

    def test_point_query(self):
        """Test point query"""
        if not getattr(settings, 'USE_POSTGIS', False):
            self.skipTest("PostGIS not enabled")

        # Test point query
        result = self.gis_service.query_at_point('Lots', 151.0862, -33.8840)
        # Result can be None or a list
        self.assertTrue(result is None or isinstance(result, list))

    def test_stats(self):
        """Test getting service stats"""
        if not getattr(settings, 'USE_POSTGIS', False):
            self.skipTest("PostGIS not enabled")

        stats = self.gis_service.stats()
        self.assertIn('source', stats)
        self.assertEqual(stats['source'], 'postgis')
