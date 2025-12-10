"""
Test script for GIS layer functionality
Run this to verify your GIS setup is working correctly
"""

import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required libraries are installed"""
    print("=" * 60)
    print("TEST 1: Checking imports...")
    print("=" * 60)

    try:
        import geopandas as gpd
        print(f"✓ GeoPandas {gpd.__version__} installed")
    except ImportError as e:
        print(f"✗ GeoPandas not found: {e}")
        return False

    try:
        import fiona
        print(f"✓ Fiona {fiona.__version__} installed")
    except ImportError as e:
        print(f"✗ Fiona not found: {e}")
        return False

    try:
        import shapely
        print(f"✓ Shapely {shapely.__version__} installed")
    except ImportError as e:
        print(f"✗ Shapely not found: {e}")
        return False

    try:
        from osgeo import gdal
        print(f"✓ GDAL {gdal.__version__} installed")
    except ImportError as e:
        print(f"✗ GDAL not found: {e}")
        return False

    print("\n✓ All required libraries installed\n")
    return True


def test_catalog():
    """Test the GIS catalog"""
    print("=" * 60)
    print("TEST 2: Loading GIS catalog...")
    print("=" * 60)

    try:
        from app.gis_config import catalog

        print(f"Total layers in catalog: {len(catalog.layers)}")
        print(f"\nCategories:")
        for category in catalog.get_all_categories():
            count = len(catalog.get_layers_by_category(category))
            available = len([l for l in catalog.get_layers_by_category(category) if l.exists()])
            print(f"  - {category}: {available}/{count} available")

        print("\n✓ Catalog loaded successfully\n")
        return True

    except Exception as e:
        print(f"✗ Error loading catalog: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_service():
    """Test the GIS service"""
    print("=" * 60)
    print("TEST 3: Testing GIS service...")
    print("=" * 60)

    try:
        from app.gis_service import gis_service

        # Get summary
        summary = gis_service.get_catalog_summary()
        print(f"Total layers: {summary['total_layers']}")
        print(f"Available layers: {summary['available_layers']}")

        # Test search
        results = gis_service.search_layers('lga')
        print(f"\nSearch for 'lga': {len(results)} results")
        for layer in results[:3]:
            print(f"  - {layer.display_name} ({layer.name})")

        print("\n✓ Service working correctly\n")
        return True

    except Exception as e:
        print(f"✗ Error testing service: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_load_layer():
    """Test loading an actual layer"""
    print("=" * 60)
    print("TEST 4: Loading sample layer...")
    print("=" * 60)

    try:
        from app.gis_service import gis_service

        # Try to find an available layer
        available = gis_service.catalog.get_available_layers()
        if not available:
            print("✗ No layers available to test")
            return False

        # Use first available layer
        test_layer = available[0]
        print(f"Testing with layer: {test_layer.display_name}")
        print(f"  Path: {test_layer.path}")
        print(f"  Format: {test_layer.format}")

        # Get layer info
        info = gis_service.get_layer_info(test_layer.name)
        if info:
            print(f"\nLayer info:")
            print(f"  Category: {info['category']}")
            print(f"  Format: {info['format']}")
            if 'feature_count' in info:
                print(f"  Features: {info['feature_count']:,}")
            if 'bounds' in info:
                print(f"  Bounds: {info['bounds']}")

        # Try to load a small bbox
        print(f"\nLoading small sample (Sydney CBD area)...")
        bbox = (151.2, -33.88, 151.22, -33.86)  # Small area in Sydney
        gdf = gis_service.load_layer(test_layer.name, bbox=bbox)

        if gdf is not None and not gdf.empty:
            print(f"✓ Loaded {len(gdf)} features")
            print(f"  Columns: {list(gdf.columns)[:5]}...")
            print(f"  CRS: {gdf.crs}")

            # Test GeoJSON conversion
            geojson = gis_service.layer_to_geojson(test_layer.name, bbox=bbox, simplify_tolerance=0.001)
            if geojson:
                print(f"✓ Converted to GeoJSON ({len(geojson)} chars)")
        else:
            print("! No features in test area (this is OK)")

        print("\n✓ Layer loading working correctly\n")
        return True

    except Exception as e:
        print(f"✗ Error loading layer: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_point_query():
    """Test querying at a point"""
    print("=" * 60)
    print("TEST 5: Testing point queries...")
    print("=" * 60)

    try:
        from app.gis_service import gis_service

        # Sydney Opera House coordinates
        lon, lat = 151.2153, -33.8568
        print(f"Querying at Sydney Opera House: {lat}, {lon}")

        # Find all layers at this point
        results = gis_service.get_layers_for_location(lon, lat)

        if results:
            print(f"\nFound features in {len(results)} categories:")
            for category, layers in results.items():
                print(f"  {category}:")
                for layer_name in layers:
                    print(f"    - {layer_name}")

            print("\n✓ Point queries working correctly\n")
        else:
            print("! No features found at point (may need more data)")
            print("✓ Point query function working\n")

        return True

    except Exception as e:
        print(f"✗ Error with point query: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    total = len(results)
    passed = sum(results.values())

    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! GIS system is ready to use.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check error messages above.")

    print("=" * 60)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("GIS LAYER SYSTEM TEST SUITE")
    print("=" * 60 + "\n")

    results = {}

    # Run tests in order
    results["Imports"] = test_imports()
    if not results["Imports"]:
        print("\n⚠️  Cannot continue without required libraries.")
        print("Please install: pip install geopandas")
        return

    results["Catalog"] = test_catalog()
    results["Service"] = test_service()
    results["Load Layer"] = test_load_layer()
    results["Point Query"] = test_point_query()

    # Print summary
    print_summary(results)


if __name__ == '__main__':
    main()
