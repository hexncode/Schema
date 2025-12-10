"""
PostGIS Database Service for GIS Data

Provides fast spatial queries using PostgreSQL/PostGIS with:
- Bbox filtering with GiST spatial indexes
- Zoom-based geometry simplification
- Point queries for property lookup
"""
import json
import logging
from typing import Optional, Dict, Tuple, List

from django.conf import settings

logger = logging.getLogger(__name__)

# Only import GIS types when PostGIS is enabled
if getattr(settings, 'USE_POSTGIS', False):
    from django.contrib.gis.geos import Polygon as GEOSPolygon
    from django.contrib.gis.geos import Point as GEOSPoint


class PostGISService:
    """GIS service using PostGIS spatial database queries."""

    SIMPLIFY_TOLERANCES = {
        10: 0.001, 12: 0.0005, 14: 0.0002,
        16: 0.00005, 18: 0.00001, 20: 0.000001,
    }

    def __init__(self):
        self._hits = 0
        self._misses = 0

    def get_tolerance(self, zoom: int) -> float:
        for z in sorted(self.SIMPLIFY_TOLERANCES.keys(), reverse=True):
            if zoom >= z:
                return self.SIMPLIFY_TOLERANCES[z]
        return 0.001

    def load_layer(self, layer_name: str, bbox: Tuple[float, float, float, float],
                   zoom_level: int = 15, limit: int = None) -> Optional[Dict]:
        """Load features from PostGIS within bounding box."""
        from atlas.models import CadastralLot, Suburb

        model_map = {
            'lots': CadastralLot, 'cadastral': CadastralLot,
            'suburb': Suburb, 'suburbs': Suburb,
        }

        layer_key = layer_name.lower().replace('_', '').replace('-', '')
        model_class = model_map.get(layer_key)

        if not model_class:
            logger.warning(f'Unknown layer: {layer_name}')
            return None

        minx, miny, maxx, maxy = bbox
        bbox_polygon = GEOSPolygon.from_bbox((minx, miny, maxx, maxy))

        queryset = model_class.objects.filter(geom__intersects=bbox_polygon)
        if limit:
            queryset = queryset[:limit]

        tolerance = self.get_tolerance(zoom_level)
        features = []

        for obj in queryset:
            try:
                geom = obj.geom
                if tolerance > 0:
                    geom = geom.simplify(tolerance, preserve_topology=True)

                if model_class == CadastralLot:
                    props = {
                        'lot_id': obj.lot_id, 'lot_number': obj.lot_number,
                        'plan_number': obj.plan_number, 'address': obj.address,
                        'area_sqm': obj.area_sqm, 'lga': obj.lga,
                    }
                else:
                    props = {
                        'suburb_name': obj.suburb_name, 'postcode': obj.postcode,
                        'lga': obj.lga, 'area_sqkm': obj.area_sqkm,
                    }

                props = {k: v for k, v in props.items() if v is not None}
                features.append({
                    'type': 'Feature', 'id': obj.pk,
                    'geometry': json.loads(geom.json), 'properties': props,
                })
            except Exception as e:
                logger.debug(f'Error processing feature {obj.pk}: {e}')

        return {
            'type': 'FeatureCollection', 'features': features,
            'metadata': {'layer': layer_name, 'count': len(features),
                        'bbox': list(bbox), 'zoom': zoom_level, 'source': 'postgis'}
        }

    def layer_to_geojson(self, layer_name: str, bbox: Tuple[float, float, float, float],
                         zoom_level: int = 15) -> Optional[str]:
        result = self.load_layer(layer_name, bbox, zoom_level)
        return json.dumps(result) if result else None

    def query_at_point(self, layer_name: str, lon: float, lat: float,
                       buffer: float = 0.0001) -> Optional[List[Dict]]:
        """Query features at a specific point."""
        from atlas.models import CadastralLot, Suburb

        model_map = {'lots': CadastralLot, 'cadastral': CadastralLot, 'suburb': Suburb}
        layer_key = layer_name.lower().replace('_', '')
        model_class = model_map.get(layer_key)

        if not model_class:
            return None

        point = GEOSPoint(lon, lat, srid=4326)
        queryset = model_class.objects.filter(geom__contains=point)

        if not queryset.exists():
            queryset = model_class.objects.filter(geom__intersects=point.buffer(buffer))

        results = []
        for obj in queryset[:10]:
            if model_class == CadastralLot:
                results.append({
                    'type': 'CadastralLot', 'lot_id': obj.lot_id,
                    'lot_number': obj.lot_number, 'plan_number': obj.plan_number,
                    'address': obj.address, 'lga': obj.lga,
                })
            else:
                results.append({
                    'type': 'Suburb', 'suburb_name': obj.suburb_name,
                    'postcode': obj.postcode, 'lga': obj.lga,
                })
        return results

    def get_catalog_summary(self) -> Dict:
        from atlas.models import CadastralLot, Suburb

        layers = []
        try:
            lots_count = CadastralLot.objects.count()
            if lots_count > 0:
                layers.append({'name': 'Lots', 'display_name': 'NSW Cadastral Lots',
                              'feature_count': lots_count, 'min_zoom': 16, 'max_zoom': 22})
        except Exception:
            pass

        try:
            suburb_count = Suburb.objects.count()
            if suburb_count > 0:
                layers.append({'name': 'Suburb', 'display_name': 'NSW Suburbs',
                              'feature_count': suburb_count, 'min_zoom': 10, 'max_zoom': 22})
        except Exception:
            pass

        return {'total_layers': len(layers), 'available_layers': len(layers),
                'source': 'postgis', 'categories': {'NSW': layers}}

    def stats(self) -> Dict:
        from atlas.models import CadastralLot, Suburb
        stats = {'source': 'postgis', 'hits': self._hits, 'misses': self._misses}
        try:
            stats['lots_count'] = CadastralLot.objects.count()
        except Exception:
            stats['lots_count'] = 0
        try:
            stats['suburb_count'] = Suburb.objects.count()
        except Exception:
            stats['suburb_count'] = 0
        return stats

    def clear_cache(self):
        pass  # PostGIS doesn't need cache clearing

    def get_cache_stats(self) -> Dict:
        return self.stats()


_postgis_service = None


def get_postgis_service() -> PostGISService:
    global _postgis_service
    if _postgis_service is None:
        _postgis_service = PostGISService()
    return _postgis_service
