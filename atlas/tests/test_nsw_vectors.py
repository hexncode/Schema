"""
Test script for NSW Vector Loader
Tests loading of NSW Lots and Buildings with zoom-based filtering
"""

from atlas.gis.nsw_vector_loader import NSWVectorLoader
from atlas.gis.config import LAYERS_PATH
from pathlib import Path

def test_nsw_loader():
    """Test the NSW Vector Loader"""

    # Initialize loader with correct path
    loader = NSWVectorLoader(LAYERS_PATH)

    print("=" * 80)
    print("NSW VECTOR LOADER TEST")
    print("=" * 80)

    # Check available layers
    print("\n1. Available Layers:")
    available = loader.get_available_layers()
    for layer_name in available:
        info = loader.get_layer_info(layer_name)
        print(f"\n   Layer: {layer_name}")
        print(f"   Display Name: {info['display_name']}")
        print(f"   Description: {info['description']}")
        print(f"   Min Zoom: {info['min_zoom']}")
        print(f"   Max Features: {info['max_features']}")
        print(f"   Path: {info['path']}")
        print(f"   Exists: {info['exists']}")

    # Test zoom-based loading
    print("\n2. Zoom-Based Loading Tests:")

    # Test at zoom 14 (too low)
    print("\n   a) Zoom 14 (should not load):")
    can_load = loader.should_load_layer('nsw_lots', 14)
    print(f"      Can load nsw_lots at zoom 14: {can_load}")

    # Test at zoom 15 (minimum for lots)
    print("\n   b) Zoom 15 (should load lots):")
    can_load = loader.should_load_layer('nsw_lots', 15)
    print(f"      Can load nsw_lots at zoom 15: {can_load}")

    # Test at zoom 16 (minimum for buildings)
    print("\n   c) Zoom 16 (should load buildings):")
    can_load = loader.should_load_layer('nsw_buildings', 16)
    print(f"      Can load nsw_buildings at zoom 16: {can_load}")

    # Test loading with bbox (Sydney CBD area)
    print("\n3. Loading Test with Bounding Box (Sydney CBD):")

    # Sydney CBD bbox (smaller area for testing)
    bbox = (151.20, -33.88, 151.21, -33.87)
    print(f"   BBox: {bbox}")

    # Try loading NSW lots at zoom 15
    print("\n   a) Loading NSW Lots at zoom 15:")
    try:
        gdf = loader.load_layer('nsw_lots', bbox, zoom_level=15)
        if gdf is not None:
            print(f"      [OK] Loaded {len(gdf)} features")
            print(f"      Columns: {list(gdf.columns)}")
            if len(gdf) > 0:
                print(f"      CRS: {gdf.crs}")
                print(f"      Sample geometry type: {gdf.geometry.iloc[0].geom_type}")
        else:
            print("      [WARN] No features found in this area")
    except Exception as e:
        print(f"      [ERROR] Error: {e}")

    # Try loading buildings at zoom 16
    print("\n   b) Loading NSW Buildings at zoom 16:")
    try:
        gdf = loader.load_layer('nsw_buildings', bbox, zoom_level=16)
        if gdf is not None:
            print(f"      [OK] Loaded {len(gdf)} features")
            print(f"      Columns: {list(gdf.columns)}")
            if len(gdf) > 0:
                print(f"      CRS: {gdf.crs}")
                print(f"      Sample geometry type: {gdf.geometry.iloc[0].geom_type}")
        else:
            print("      [WARN] No features found in this area")
    except Exception as e:
        print(f"      [ERROR] Error: {e}")

    # Test GeoJSON conversion
    print("\n4. GeoJSON Conversion Test:")
    try:
        geojson = loader.layer_to_geojson('nsw_lots', bbox, zoom_level=15)
        if geojson:
            import json
            data = json.loads(geojson)
            feature_count = len(data.get('features', []))
            print(f"   [OK] Converted to GeoJSON: {feature_count} features")
            print(f"   GeoJSON type: {data.get('type')}")
        else:
            print("   [WARN] No GeoJSON generated")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")

    # Test point query
    print("\n5. Point Query Test (Sydney Opera House):")
    lon, lat = 151.2153, -33.8568
    print(f"   Coordinates: {lon}, {lat}")

    try:
        features = loader.query_features_at_point('nsw_lots', lon, lat)
        if features is not None and not features.empty:
            print(f"   [OK] Found {len(features)} lot(s)")
            for idx, row in features.iterrows():
                print(f"      Lot attributes: {dict(row.drop('geometry'))}")
        else:
            print("   [WARN] No lots found at this point")
    except Exception as e:
        print(f"   [ERROR] Error: {e}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    test_nsw_loader()
