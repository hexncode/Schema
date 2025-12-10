"""
Atlas GIS views - Django views supporting both PostGIS and file-based GIS backends
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from django.conf import settings
import json

from atlas.gis.service import gis_service

# Check if PostGIS mode is enabled
USE_POSTGIS = getattr(settings, 'USE_POSTGIS', False)

# Only import LAYERS_PATH if not using PostGIS
if not USE_POSTGIS:
    from atlas.gis.config import LAYERS_PATH


def map_view(request):
    """GIS Map page"""
    return render(request, 'atlas/map.html')


@require_http_methods(["POST"])
def search_property(request):
    """Search property by Lot/DP number"""
    try:
        data = json.loads(request.body)
        lot = data.get('lot')
        dp = data.get('dp')

        # TODO: Implement search in geopackage
        # For now, return placeholder
        return JsonResponse({
            'success': True,
            'properties': [{
                'lot': lot,
                'dp': dp,
                'address': f'Lot {lot} DP {dp}',
                'lat': -33.8688,
                'lon': 151.2093
            }]
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
def property_details(request):
    """Get property details at point"""
    try:
        data = json.loads(request.body)
        lat = float(data['lat'])
        lon = float(data['lon'])

        if USE_POSTGIS:
            # Use PostGIS service
            results = gis_service.query_at_point('Lots', lon, lat)
            if results:
                lot_data = results[0]
                return JsonResponse({
                    'success': True,
                    'property': {
                        'lot': lot_data.get('lot_number'),
                        'dp': lot_data.get('plan_number'),
                        'address': lot_data.get('address'),
                        'area': lot_data.get('area_sqm'),
                        'lga': lot_data.get('lga'),
                        'lat': lat,
                        'lon': lon
                    }
                })
        else:
            # Use file-based service
            lot_gdf = gis_service.query_features_at_point('Lots', lon, lat)
            if lot_gdf is not None and not lot_gdf.empty:
                lot_data = lot_gdf.iloc[0]
                return JsonResponse({
                    'success': True,
                    'property': {
                        'lot': lot_data.get('lotnumber'),
                        'dp': lot_data.get('plannumber'),
                        'address': lot_data.get('address'),
                        'area': lot_data.get('planlotare'),
                        'council': lot_data.get('councilnam'),
                        'lga': lot_data.get('lganame'),
                        'lat': lat,
                        'lon': lon
                    }
                })

        return JsonResponse({
            'success': False,
            'error': 'No property found at location'
        }, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["POST"])
def properties_in_bounds(request):
    """Get properties in bounding box"""
    try:
        data = json.loads(request.body)
        north = float(data['north'])
        south = float(data['south'])
        east = float(data['east'])
        west = float(data['west'])

        bbox = (west, south, east, north)

        if USE_POSTGIS:
            # Use PostGIS service
            result = gis_service.load_layer('Lots', bbox, zoom_level=16, limit=50)
            if result and 'features' in result:
                properties = []
                for feature in result['features'][:50]:
                    props = feature.get('properties', {})
                    geom = feature.get('geometry', {})
                    # Get centroid from geometry
                    lat, lon = None, None
                    if geom.get('type') == 'MultiPolygon' and geom.get('coordinates'):
                        coords = geom['coordinates'][0][0]
                        if coords:
                            lon = sum(c[0] for c in coords) / len(coords)
                            lat = sum(c[1] for c in coords) / len(coords)
                    properties.append({
                        'lot': props.get('lot_number'),
                        'dp': props.get('plan_number'),
                        'address': props.get('address'),
                        'lat': lat,
                        'lon': lon,
                    })
                return JsonResponse({'success': True, 'properties': properties})
            return JsonResponse({'success': True, 'properties': []})
        else:
            # Use file-based service
            import geopandas as gpd
            lots_path = LAYERS_PATH / 'NSW_Lots.gpkg'
            if lots_path.exists():
                gdf = gpd.read_file(lots_path, bbox=bbox)
                properties = []
                for _, lot in gdf.head(50).iterrows():
                    properties.append({
                        'lot': lot.get('lotnumber'),
                        'dp': lot.get('plannumber'),
                        'address': lot.get('address'),
                        'lat': lot.geometry.centroid.y if lot.geometry else None,
                        'lon': lot.geometry.centroid.x if lot.geometry else None,
                    })
                return JsonResponse({'success': True, 'properties': properties})
            return JsonResponse({'success': False, 'error': 'Layer not found'}, status=404)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
@cache_page(60 * 5)
def get_gis_catalog(request):
    """Get GIS layer catalog"""
    catalog = gis_service.get_catalog_summary()
    return JsonResponse({'success': True, 'catalog': catalog})


@require_http_methods(["GET"])
def get_gis_layer(request, layer_name):
    """Get GeoJSON for layer"""
    try:
        bbox_param = request.GET.get('bbox')
        if not bbox_param:
            return JsonResponse({'success': False, 'error': 'bbox required'}, status=400)

        bbox = tuple(map(float, bbox_param.split(',')))
        zoom_level = int(request.GET.get('zoom', 15))

        geojson = gis_service.layer_to_geojson(layer_name, bbox, zoom_level=zoom_level)

        if geojson is None:
            return JsonResponse({'success': False, 'error': 'Layer not found'}, status=404)

        return JsonResponse(json.loads(geojson), safe=False)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_gis_layer_info(request, layer_name):
    """Get layer metadata"""
    if USE_POSTGIS:
        catalog = gis_service.get_catalog_summary()
        for category, layers in catalog.get('categories', {}).items():
            for layer in layers:
                if layer['name'].lower() == layer_name.lower():
                    return JsonResponse({
                        'success': True,
                        'layer': {
                            'name': layer['name'],
                            'display_name': layer['display_name'],
                            'min_zoom': layer.get('min_zoom', 16),
                            'max_zoom': layer.get('max_zoom', 22),
                            'feature_count': layer.get('feature_count', 0),
                            'source': 'postgis'
                        }
                    })
        return JsonResponse({'success': False, 'error': 'Layer not found'}, status=404)
    else:
        layer = gis_service.layer_manager.get_layer(layer_name)
        if not layer:
            return JsonResponse({'success': False, 'error': 'Layer not found'}, status=404)
        return JsonResponse({
            'success': True,
            'layer': {
                'name': layer_name,
                'display_name': layer.display_name,
                'min_zoom': layer.min_zoom,
                'exists': layer.path.exists()
            }
        })


@require_http_methods(["GET", "POST"])
def query_gis_point(request):
    """Query GIS at point - returns lot info and planning controls"""
    try:
        if request.method == 'GET':
            lat = float(request.GET.get('lat'))
            lon = float(request.GET.get('lon'))
        else:
            data = json.loads(request.body)
            lat = float(data['lat'])
            lon = float(data['lon'])

        results = {}
        planning_info = {
            'zoning': None,
            'zoningName': None,
            'fsr': None,
            'height': None,
            'minLotSize': None,
            'heritage': None,
            'flood': None,
            'bushfire': None,
            'acid': None,
            'contaminated': None,
            'additionalInfo': None,
            'planningPortalLink': 'https://www.planningportal.nsw.gov.au/spatialviewer/'
        }

        if USE_POSTGIS:
            # Use PostGIS service
            lot_results = gis_service.query_at_point('Lots', lon, lat)
            if lot_results:
                lot_data = lot_results[0]
                results['lot'] = {
                    'type': 'Feature',
                    'properties': {
                        'lot': lot_data.get('lot_number'),
                        'dp': lot_data.get('plan_number'),
                        'address': lot_data.get('address'),
                        'lganame': lot_data.get('lga'),
                    }
                }
                planning_info['additionalInfo'] = f"LGA: {lot_data.get('lga')}"
        else:
            # Use file-based service
            lot_gdf = gis_service.query_features_at_point('Lots', lon, lat)
            if lot_gdf is not None and not lot_gdf.empty:
                lot_data = lot_gdf.iloc[0]
                results['lot'] = {
                    'type': 'Feature',
                    'properties': {
                        'lot': lot_data.get('lotnumber'),
                        'dp': lot_data.get('plannumber'),
                        'address': lot_data.get('address'),
                        'councilnam': lot_data.get('councilnam'),
                        'lganame': lot_data.get('lganame'),
                    }
                }
                planning_info['additionalInfo'] = f"LGA: {lot_data.get('lganame')}"

        # Query NSW Planning Portal for planning controls
        planning_data = query_nsw_planning_portal(lat, lon)
        planning_info.update(planning_data)

        return JsonResponse({
            'success': True,
            'results': results,
            'planning': planning_info
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def query_nsw_planning_portal(lat, lon):
    """
    Query NSW Planning Portal WMS for planning controls at a point.
    Returns zoning, FSR, height limits, heritage, flood, bushfire etc.
    """
    import requests
    from urllib.parse import urlencode

    planning_data = {}

    # NSW Planning Portal ArcGIS REST API endpoint
    base_url = 'https://mapprod3.environment.nsw.gov.au/arcgis/rest/services/Planning/EPI_Primary_Planning_Layers/MapServer'

    # Layer IDs in NSW Planning Portal:
    # 1 = Land Zoning
    # 2 = Floor Space Ratio
    # 3 = Height of Buildings
    # 4 = Minimum Lot Size
    # 5 = Lot Size (Additional)
    # 6 = Land Reservation Acquisition
    # 7 = Key Sites
    # 8 = Heritage
    # 9 = Flood Planning
    # 10 = Riparian Lands
    # 14 = Bush Fire Prone Land
    # 15 = Acid Sulfate Soils

    layers_to_query = [
        {'id': 1, 'name': 'zoning', 'fields': ['LAY_CLASS', 'SYM_CODE', 'ZONE_CODE', 'LAY_NAME', 'ZONE_NAME', 'EPI_NAME']},
        {'id': 2, 'name': 'fsr', 'fields': ['LAY_CLASS', 'FSR', 'FSR_VALUE']},
        {'id': 3, 'name': 'height', 'fields': ['LAY_CLASS', 'HOB', 'MAX_B_H', 'HEIGHT']},
        {'id': 4, 'name': 'minLotSize', 'fields': ['LAY_CLASS', 'LOT_SIZE', 'MIN_LOT']},
        {'id': 8, 'name': 'heritage', 'fields': ['HER_NAME', 'HERITAGE', 'SIGNIFICANCE', 'LAY_CLASS']},
        {'id': 9, 'name': 'flood', 'fields': ['FLOOD', 'FLD_ZONE', 'LAY_CLASS', 'CATEGORY']},
        {'id': 14, 'name': 'bushfire', 'fields': ['CATEGORY', 'BF_ZONE', 'BUSHFIRE', 'LAY_CLASS']},
        {'id': 15, 'name': 'acid', 'fields': ['ASS_CLASS', 'ACID', 'CLASS', 'LAY_CLASS']},
    ]

    # Create a small buffer around the point for the query
    buffer = 0.0001  # ~11 meters
    geometry = {
        'xmin': lon - buffer,
        'ymin': lat - buffer,
        'xmax': lon + buffer,
        'ymax': lat + buffer,
        'spatialReference': {'wkid': 4326}
    }

    for layer in layers_to_query:
        try:
            # Build identify request for each layer
            params = {
                'f': 'json',
                'geometry': json.dumps(geometry),
                'geometryType': 'esriGeometryEnvelope',
                'sr': '4326',
                'layers': f'all:{layer["id"]}',
                'tolerance': '3',
                'mapExtent': f'{lon-0.01},{lat-0.01},{lon+0.01},{lat+0.01}',
                'imageDisplay': '400,400,96',
                'returnGeometry': 'false',
            }

            url = f'{base_url}/identify?{urlencode(params)}'
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                data = response.json()

                if 'results' in data and len(data['results']) > 0:
                    attrs = data['results'][0].get('attributes', {})

                    if layer['name'] == 'zoning':
                        zone_code = attrs.get('LAY_CLASS') or attrs.get('SYM_CODE') or attrs.get('ZONE_CODE')
                        if zone_code:
                            planning_data['zoning'] = zone_code
                            planning_data['zoningName'] = attrs.get('LAY_NAME') or attrs.get('ZONE_NAME') or attrs.get('EPI_NAME')

                    elif layer['name'] == 'fsr':
                        fsr_val = attrs.get('LAY_CLASS') or attrs.get('FSR') or attrs.get('FSR_VALUE')
                        if fsr_val:
                            # Extract numeric FSR value
                            import re
                            match = re.search(r'(\d+\.?\d*)', str(fsr_val))
                            if match:
                                planning_data['fsr'] = float(match.group(1))

                    elif layer['name'] == 'height':
                        hob_val = attrs.get('LAY_CLASS') or attrs.get('HOB') or attrs.get('MAX_B_H') or attrs.get('HEIGHT')
                        if hob_val:
                            import re
                            match = re.search(r'(\d+\.?\d*)', str(hob_val))
                            if match:
                                planning_data['height'] = float(match.group(1))

                    elif layer['name'] == 'minLotSize':
                        lot_val = attrs.get('LAY_CLASS') or attrs.get('LOT_SIZE') or attrs.get('MIN_LOT')
                        if lot_val:
                            import re
                            match = re.search(r'(\d+)', str(lot_val))
                            if match:
                                planning_data['minLotSize'] = int(match.group(1))

                    elif layer['name'] == 'heritage':
                        her_val = attrs.get('HER_NAME') or attrs.get('HERITAGE') or attrs.get('SIGNIFICANCE') or attrs.get('LAY_CLASS')
                        if her_val and str(her_val).strip():
                            planning_data['heritage'] = str(her_val)

                    elif layer['name'] == 'flood':
                        flood_val = attrs.get('CATEGORY') or attrs.get('FLOOD') or attrs.get('FLD_ZONE') or attrs.get('LAY_CLASS')
                        if flood_val and str(flood_val).strip():
                            planning_data['flood'] = str(flood_val)

                    elif layer['name'] == 'bushfire':
                        bf_val = attrs.get('CATEGORY') or attrs.get('BF_ZONE') or attrs.get('BUSHFIRE') or attrs.get('LAY_CLASS')
                        if bf_val and str(bf_val).strip():
                            planning_data['bushfire'] = str(bf_val)

                    elif layer['name'] == 'acid':
                        acid_val = attrs.get('ASS_CLASS') or attrs.get('CLASS') or attrs.get('ACID') or attrs.get('LAY_CLASS')
                        if acid_val and str(acid_val).strip():
                            planning_data['acid'] = str(acid_val)

        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.RequestException:
            continue
        except Exception:
            continue

    return planning_data


@require_http_methods(["GET"])
def search_gis_layers(request):
    """Search layers"""
    query = request.GET.get('q', '').lower()

    if not query:
        return JsonResponse({'success': False, 'error': 'Query required'}, status=400)

    results = []
    if USE_POSTGIS:
        catalog = gis_service.get_catalog_summary()
        for category, layers in catalog.get('categories', {}).items():
            for layer in layers:
                if query in layer['name'].lower() or query in layer['display_name'].lower():
                    results.append({
                        'name': layer['name'],
                        'display_name': layer['display_name'],
                        'feature_count': layer.get('feature_count', 0)
                    })
    else:
        results = [
            {
                'name': layer.name,
                'display_name': layer.display_name,
                'exists': layer.path.exists()
            }
            for layer in gis_service.layer_manager.list_layers()
            if query in layer.name.lower() or query in layer.display_name.lower()
        ]

    return JsonResponse({'success': True, 'results': results, 'count': len(results)})


@require_http_methods(["GET"])
def get_cache_stats(request):
    """Get GIS cache statistics"""
    stats = gis_service.get_cache_stats()
    return JsonResponse({'success': True, 'cache': stats})


@require_http_methods(["POST"])
def clear_cache(request):
    """Clear GIS cache (admin only in production)"""
    try:
        gis_service.clear_cache()
        return JsonResponse({'success': True, 'message': 'Cache cleared successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@require_http_methods(["GET"])
def get_layer_tiles(request, layer_name):
    """Get tile grid for a layer viewport - used for chunked loading"""
    try:
        bbox_param = request.GET.get('bbox')
        if not bbox_param:
            return JsonResponse({'success': False, 'error': 'bbox required'}, status=400)

        bbox = tuple(map(float, bbox_param.split(',')))

        if USE_POSTGIS:
            # PostGIS doesn't need tiles, return bbox as single "tile"
            tiles = [{
                'id': 'full',
                'bbox': list(bbox)
            }]
        else:
            # Generate tiles for this viewport
            tiles = gis_service.layer_manager.generate_tiles(bbox)

        return JsonResponse({
            'success': True,
            'tiles': tiles,
            'tile_count': len(tiles)
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@require_http_methods(["GET"])
def get_layer_tile(request, layer_name, tile_id):
    """Get GeoJSON data for a specific tile"""
    try:
        bbox_param = request.GET.get('bbox')
        if not bbox_param:
            return JsonResponse({'success': False, 'error': 'bbox required'}, status=400)

        bbox = tuple(map(float, bbox_param.split(',')))
        zoom = int(request.GET.get('zoom', 15))

        # Load tile data
        geojson = gis_service.layer_to_geojson(layer_name, bbox, zoom_level=zoom)

        if geojson is None:
            return JsonResponse({'type': 'FeatureCollection', 'features': []})

        return JsonResponse(json.loads(geojson), safe=False)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
