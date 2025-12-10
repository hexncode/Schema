"""
GIS Module - PostGIS-First Architecture

Primary: PostGIS database backend (set USE_POSTGIS=True)
Fallback: File-based GeoPackage service (for development)

Usage:
    from atlas.gis import gis_service

    # Query features
    result = gis_service.load_layer('Lots', bbox, zoom_level=16)

    # Get catalog
    catalog = gis_service.get_catalog_summary()

Import GIS data into PostGIS:
    USE_POSTGIS=True python manage.py import_gis_data
"""

from .service import gis_service
from .config import LAYERS_PATH, GIS_BASE_PATH

__all__ = [
    'gis_service',
    'LAYERS_PATH',
    'GIS_BASE_PATH',
]
