"""
GIS Service Module - PostGIS-First Architecture

RECOMMENDED: Set USE_POSTGIS=True in your environment for production.
- GIS data is stored in PostgreSQL/PostGIS database
- Use `python manage.py import_gis_data` to import GeoPackage files
- Fast spatial queries with GiST indexes

Development fallback (USE_POSTGIS=False):
- Reads directly from GeoPackage files in atlas/gis/Layers/
- Requires large files present locally (not in git)
"""

import logging
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta

from django.conf import settings

logger = logging.getLogger(__name__)

USE_POSTGIS = getattr(settings, 'USE_POSTGIS', False)


class GISCache:
    """LRU cache with TTL for GIS query results."""

    def __init__(self, ttl_minutes: int = 15, max_items: int = 100, max_size_mb: float = 50):
        self._cache: Dict[str, any] = {}
        self._timestamps: Dict[str, datetime] = {}
        self._access_times: Dict[str, datetime] = {}
        self._sizes: Dict[str, int] = {}
        self._ttl = timedelta(minutes=ttl_minutes)
        self._max_items = max_items
        self._max_size_bytes = int(max_size_mb * 1024 * 1024)
        self._current_size_bytes = 0
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[any]:
        if key not in self._cache:
            self._misses += 1
            return None
        if datetime.now() - self._timestamps[key] > self._ttl:
            self._evict(key)
            self._misses += 1
            return None
        self._access_times[key] = datetime.now()
        self._hits += 1
        return self._cache[key]

    def set(self, key: str, value: any):
        import sys
        size = sys.getsizeof(value)
        while (len(self._cache) >= self._max_items or
               self._current_size_bytes + size > self._max_size_bytes):
            if not self._cache:
                break
            self._evict_lru()
        self._cache[key] = value
        self._timestamps[key] = datetime.now()
        self._access_times[key] = datetime.now()
        self._sizes[key] = size
        self._current_size_bytes += size

    def _evict(self, key: str):
        if key in self._cache:
            self._current_size_bytes -= self._sizes.get(key, 0)
            del self._cache[key]
            del self._timestamps[key]
            del self._access_times[key]
            self._sizes.pop(key, None)

    def _evict_lru(self):
        if not self._access_times:
            return
        lru_key = min(self._access_times, key=self._access_times.get)
        self._evict(lru_key)

    def clear(self):
        self._cache.clear()
        self._timestamps.clear()
        self._access_times.clear()
        self._sizes.clear()
        self._current_size_bytes = 0

    def stats(self) -> Dict:
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        return {
            'items': len(self._cache),
            'max_items': self._max_items,
            'size_mb': round(self._current_size_bytes / (1024 * 1024), 2),
            'hits': self._hits,
            'misses': self._misses,
            'hit_rate': f"{hit_rate:.1f}%"
        }


class FileGISService:
    """File-based GIS service using GeoPackage files. For development/import only."""

    def __init__(self):
        self._cache = GISCache()
        self.layer_manager = None
        try:
            from atlas.gis.config import LAYERS_PATH
            from atlas.gis.layer_manager import LayerManager
            self.layer_manager = LayerManager(LAYERS_PATH)
            logger.info(f"FileGISService: {len(self.layer_manager.layers)} layers available")
        except Exception as e:
            logger.warning(f"FileGISService: LayerManager failed: {e}")

    def load_layer(self, layer_name: str, bbox: Tuple[float, float, float, float],
                   zoom_level: int = 15, **kwargs):
        if not self.layer_manager:
            return None
        return self.layer_manager.load_layer(layer_name, bbox, zoom_level)

    def layer_to_geojson(self, layer_name: str, bbox: Tuple[float, float, float, float],
                         zoom_level: int = 15) -> Optional[str]:
        if not self.layer_manager:
            return None
        return self.layer_manager.layer_to_geojson(layer_name, bbox, zoom_level)

    def query_at_point(self, layer_name: str, lon: float, lat: float,
                       buffer: float = 0.0001):
        if not self.layer_manager:
            return None
        return self.layer_manager.query_at_point(layer_name, lon, lat, buffer)

    def get_catalog_summary(self) -> Dict:
        if not self.layer_manager:
            return {'total_layers': 0, 'available_layers': 0, 'categories': {}}
        layers = self.layer_manager.list_layers()
        categories = {}
        for layer in layers:
            if layer.category not in categories:
                categories[layer.category] = []
            categories[layer.category].append({
                'name': layer.name,
                'display_name': layer.display_name,
                'min_zoom': layer.min_zoom,
                'max_zoom': layer.max_zoom
            })
        return {
            'total_layers': len(layers),
            'available_layers': len(layers),
            'source': 'file',
            'categories': categories
        }

    def clear_cache(self):
        self._cache.clear()

    def get_cache_stats(self) -> Dict:
        return self._cache.stats()

    def stats(self) -> Dict:
        return {'source': 'file', **self._cache.stats()}


def _create_gis_service():
    """Factory: create appropriate GIS service based on configuration."""
    if USE_POSTGIS:
        logger.info('GIS: Using PostGIS database')
        try:
            from atlas.gis.db_service import get_postgis_service
            return get_postgis_service()
        except Exception as e:
            logger.error(f'GIS: PostGIS failed: {e}, falling back to file-based')
    else:
        logger.info('GIS: Using file-based service (set USE_POSTGIS=True for production)')
    return FileGISService()


# Global singleton
gis_service = _create_gis_service()
