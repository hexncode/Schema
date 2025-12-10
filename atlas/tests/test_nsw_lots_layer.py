"""
Test script to verify the NSW Lots layer from geodatabase loads correctly
"""
import sys
import io
from pathlib import Path

# Set UTF-8 encoding for console output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.gis_service import gis_service
from app.gis_config import catalog

def test_nsw_lots_layer():
    """Test loading the NSW lots layer from geodatabase"""

    print("=" * 80)
    print("Testing NSW Lots Layer from Geodatabase")
    print("=" * 80)

    # Check if layer exists in catalog
    layer = catalog.get_layer('nsw_lots_all')

    if not layer:
        print("❌ ERROR: Layer 'nsw_lots_all' not found in catalog")
        return False

    print(f"✓ Layer found in catalog: {layer.display_name}")
    print(f"  Path: {layer.full_path}")
    print(f"  Format: {layer.format}")
    print(f"  Category: {layer.category}")
    print(f"  Min Zoom: {layer.min_zoom}")
    print(f"  Style: {layer.style}")
    print()

    # Check if file exists
    if not layer.exists():
        print(f"❌ ERROR: Geodatabase file does not exist at: {layer.full_path}")
        return False

    print(f"✓ Geodatabase file exists")
    print()

    # Try to load layer info (doesn't load geometry, just metadata)
    print("Loading layer metadata...")
    layer_info = gis_service.get_layer_info('nsw_lots_all')

    if not layer_info:
        print("❌ ERROR: Could not load layer metadata")
        return False

    print(f"✓ Layer metadata loaded successfully")
    if 'feature_count' in layer_info:
        print(f"  Total features: {layer_info['feature_count']:,}")
    if 'crs' in layer_info:
        print(f"  CRS: {layer_info['crs']}")
    if 'bounds' in layer_info:
        bounds = layer_info['bounds']
        print(f"  Bounds: ({bounds['minx']:.4f}, {bounds['miny']:.4f}) to ({bounds['maxx']:.4f}, {bounds['maxy']:.4f})")
    print()

    # Test loading a small sample with bbox (Sydney CBD area)
    print("Testing bbox loading (Sydney CBD area)...")
    sydney_bbox = (151.19, -33.88, 151.23, -33.86)  # Small area around Sydney

    try:
        gdf = gis_service.load_layer('nsw_lots_all', bbox=sydney_bbox)

        if gdf is None or gdf.empty:
            print("⚠ WARNING: No features loaded in bbox (this might be expected if no lots in that area)")
        else:
            print(f"✓ Successfully loaded {len(gdf)} features in bbox")
            print(f"  CRS: {gdf.crs}")
            print(f"  Columns: {list(gdf.columns)}")

            # Show sample feature
            if len(gdf) > 0:
                print("\n  Sample feature:")
                sample = gdf.iloc[0]
                for col in ['lot', 'lotnumber', 'planno', 'planlabel', 'address', 'calcarea', 'lga']:
                    if col in sample:
                        print(f"    {col}: {sample[col]}")
        print()

    except Exception as e:
        print(f"❌ ERROR loading layer with bbox: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    # Test GeoJSON export
    print("Testing GeoJSON export...")
    try:
        geojson = gis_service.layer_to_geojson('nsw_lots_all', bbox=sydney_bbox, simplify_tolerance=0.00001)

        if geojson:
            print(f"✓ GeoJSON export successful")
            print(f"  Size: {len(geojson):,} characters")
        else:
            print("⚠ WARNING: GeoJSON export returned None")
        print()

    except Exception as e:
        print(f"❌ ERROR exporting to GeoJSON: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

    print("=" * 80)
    print("✓ All tests passed successfully!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("1. Start the Flask application: python run.py")
    print("2. Navigate to http://localhost:5000/map")
    print("3. Toggle on 'NSW Property Lots (All NSW)' in the layer control")
    print("4. Zoom to level 15+ to see the lots layer load")
    print()

    return True


if __name__ == '__main__':
    try:
        success = test_nsw_lots_layer()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
