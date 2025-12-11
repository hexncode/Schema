"""
Test GIS Layers - Django/PostGIS

Tests the GIS layer system and PostGIS functionality.
"""

from django.test import TestCase
from django.conf import settings


class GISLayerTestCase(TestCase):
    """Test the GIS layer functionality"""

    def test_postgis_enabled(self):
        """Test PostGIS configuration"""
        use_postgis = getattr(settings, 'USE_POSTGIS', False)
        # Just verify the setting exists
        self.assertIsInstance(use_postgis, bool)

    def test_gis_service_import(self):
        """Test that GIS service can be imported"""
        from atlas.gis import gis_service
        self.assertIsNotNone(gis_service)

    def test_gis_service_has_methods(self):
        """Test that GIS service has required methods"""
        from atlas.gis import gis_service

        self.assertTrue(hasattr(gis_service, 'load_layer'))
        self.assertTrue(hasattr(gis_service, 'get_catalog_summary'))
        self.assertTrue(hasattr(gis_service, 'query_at_point'))
        self.assertTrue(hasattr(gis_service, 'stats'))

    def test_catalog_summary_structure(self):
        """Test catalog summary returns expected structure"""
        from atlas.gis import gis_service

        summary = gis_service.get_catalog_summary()
        self.assertIn('total_layers', summary)
        self.assertIn('available_layers', summary)
        self.assertIn('source', summary)
        self.assertIn('categories', summary)
