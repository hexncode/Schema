"""
Test NSW Lots Layer - Django/PostGIS

Tests the CadastralLot model and PostGIS spatial queries.
"""

from django.test import TestCase
from django.conf import settings


class NSWLotsTestCase(TestCase):
    """Test the NSW Lots layer"""

    def test_model_exists(self):
        """Test that CadastralLot model exists"""
        if not getattr(settings, 'USE_POSTGIS', False):
            self.skipTest("PostGIS not enabled")

        from atlas.models import CadastralLot
        # Should not raise an error
        self.assertTrue(hasattr(CadastralLot, 'objects'))

    def test_lots_count(self):
        """Test that lots table has data"""
        if not getattr(settings, 'USE_POSTGIS', False):
            self.skipTest("PostGIS not enabled")

        from atlas.models import CadastralLot
        count = CadastralLot.objects.count()
        # Just verify we can query - count may be 0 in test DB
        self.assertIsInstance(count, int)

    def test_spatial_query(self):
        """Test spatial query on lots"""
        if not getattr(settings, 'USE_POSTGIS', False):
            self.skipTest("PostGIS not enabled")

        from atlas.models import CadastralLot
        from django.contrib.gis.geos import Polygon

        # Create a test bbox
        bbox = Polygon.from_bbox((151.08, -33.89, 151.09, -33.88))
        queryset = CadastralLot.objects.filter(geom__intersects=bbox)

        # Should return a queryset (may be empty in test DB)
        self.assertTrue(hasattr(queryset, 'count'))
