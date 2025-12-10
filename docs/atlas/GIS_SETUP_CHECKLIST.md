# GIS Layer System - Setup Checklist

Use this checklist to set up and verify your GIS layer system.

## Installation Checklist

### Step 1: Install Dependencies ⬜

Choose ONE method:

**Option A: Conda (Recommended for Windows)**
```bash
⬜ conda install -c conda-forge geopandas
```

**Option B: Pip with Pre-built Wheels**
```bash
⬜ Download GDAL wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/
⬜ Download Fiona wheel from same site
⬜ pip install GDAL-*.whl
⬜ pip install Fiona-*.whl
⬜ pip install geopandas
```

### Step 2: Verify Installation ⬜

```bash
⬜ python -c "import geopandas; print(geopandas.__version__)"
⬜ python -c "from osgeo import gdal; print(gdal.__version__)"
```

Should show version numbers without errors.

## Testing Checklist

### Step 3: Run Automated Tests ⬜

```bash
⬜ cd X:\Projects\A_Valuation\_Apps\Appraise.ai
⬜ python test_gis_layers.py
```

Expected results:
- ⬜ Test 1: Imports - PASS
- ⬜ Test 2: Catalog - PASS
- ⬜ Test 3: Service - PASS
- ⬜ Test 4: Load Layer - PASS
- ⬜ Test 5: Point Query - PASS

### Step 4: Start Flask Application ⬜

```bash
⬜ python run.py
```

Application should start without errors.

### Step 5: Test API Endpoints ⬜

Open browser or use curl:

**Catalog Endpoint**
```bash
⬜ http://localhost:5000/api/gis/catalog
```
Should return JSON with catalog data.

**Layer Info Endpoint**
```bash
⬜ http://localhost:5000/api/gis/layer/lga_2022/info
```
Should return layer metadata.

**Load Layer Endpoint**
```bash
⬜ http://localhost:5000/api/gis/layer/lga_2022?simplify=0.001
```
Should return GeoJSON data.

**Search Endpoint**
```bash
⬜ http://localhost:5000/api/gis/search?q=suburb
```
Should return search results.

## Verification Checklist

### Step 6: Verify Data Files ⬜

Check that GIS data exists:

```bash
⬜ dir "app\gis\Layers\Geographic areas"
⬜ dir "app\gis\Layers\NSW LGA (Sixmaps)"
⬜ dir "app\gis\Layers\ABS Areas"
```

Should show directories with .gpkg, .shp files.

### Step 7: Check Catalog Coverage ⬜

Using Python:
```python
from app.gis_service import gis_service
summary = gis_service.get_catalog_summary()
print(f"Total layers: {summary['total_layers']}")
print(f"Available: {summary['available_layers']}")
```

Expected:
- ⬜ Total layers: ~150
- ⬜ Available layers: 100+ (depending on data)

### Step 8: Test Sample Layer ⬜

Using Python:
```python
from app.gis_service import gis_service

# Load LGA layer
⬜ gdf = gis_service.load_layer('lga_2022')
⬜ print(f"Loaded {len(gdf)} features")

# Convert to GeoJSON
⬜ geojson = gis_service.layer_to_geojson('lga_2022', simplify_tolerance=0.001)
⬜ print(f"GeoJSON size: {len(geojson)} characters")
```

## Integration Checklist

### Step 9: Frontend Integration ⬜

Add to your map.html:

```javascript
⬜ Create loadGISLayer() function
⬜ Test loading one layer (e.g., suburbs_2021)
⬜ Add layer toggle controls
⬜ Implement layer styling
⬜ Add zoom-level management
```

### Step 10: Layer Controls ⬜

Add UI elements:
- ⬜ Layer selection dropdown
- ⬜ Category filters
- ⬜ Layer visibility toggles
- ⬜ Opacity controls
- ⬜ Layer legend

## Production Checklist

### Step 11: Performance Optimization ⬜

Implement:
- ⬜ Bounding box filtering on all layer requests
- ⬜ Geometry simplification for overview maps
- ⬜ Zoom-level based layer loading
- ⬜ Layer caching (future)

### Step 12: Error Handling ⬜

Add:
- ⬜ Error messages for missing layers
- ⬜ Loading indicators
- ⬜ Fallback for failed requests
- ⬜ User notifications

### Step 13: Documentation ⬜

Review:
- ⬜ Read GIS_LAYERS_README.md
- ⬜ Read GIS_QUICKSTART.md
- ⬜ Review GIS_IMPLEMENTATION_SUMMARY.md
- ⬜ Bookmark useful layer combinations

## Common Issues & Solutions

### Issue 1: "ModuleNotFoundError: No module named 'geopandas'"
```bash
✓ Solution: Install geopandas
   conda install -c conda-forge geopandas
```

### Issue 2: "Layer not found" in API
```bash
✓ Check: /api/gis/layer/layer_name/info
✓ Verify file exists in catalog
✓ Check file path in gis_config.py
```

### Issue 3: Map shows data in wrong location
```bash
✓ Data is auto-transformed to WGS84
✓ Check original CRS of source data
✓ Verify coordinates: Sydney is ~-33.87, 151.21
```

### Issue 4: Slow layer loading
```bash
✓ Add bbox parameter to limit extent
✓ Increase simplify tolerance (0.001 or higher)
✓ Use appropriate zoom levels
✓ Consider vector tiles for very large datasets
```

## Quick Reference

### Key Files
- `app/gis_config.py` - Layer catalog
- `app/gis_service.py` - Data loading service
- `app/routes/main.py` - API endpoints (lines 748+)
- `test_gis_layers.py` - Test suite

### Key Endpoints
- `/api/gis/catalog` - Get all layers
- `/api/gis/layer/<name>` - Load layer
- `/api/gis/layer/<name>/info` - Layer info
- `/api/gis/query/point` - Spatial query
- `/api/gis/search?q=<query>` - Search layers

### Layer Categories
1. Administrative (LGA, suburbs, postcodes)
2. Statistical Areas (SA1-SA4, mesh blocks)
3. Cadastral (property lots, easements)
4. Transport (roads, railways)
5. Hydrology (water features)
6. Topography (contours, heights)
7. Buildings (footprints)
8. Utilities (power, pipelines)

## Success Criteria

Your GIS system is fully operational when:

- ✅ All tests pass (test_gis_layers.py)
- ✅ API endpoints return data
- ✅ At least 50% of layers load successfully
- ✅ Can query layers at a point
- ✅ Can load layers onto map
- ✅ Frontend displays GIS layers correctly

## Next Steps After Setup

1. ⬜ Explore available layers in catalog
2. ⬜ Test different layer combinations
3. ⬜ Add layer controls to map interface
4. ⬜ Implement spatial analysis features
5. ⬜ Integrate with property valuation workflows

## Support Resources

- **Documentation**: GIS_LAYERS_README.md
- **Quick Start**: GIS_QUICKSTART.md
- **Test Suite**: test_gis_layers.py
- **Implementation Details**: GIS_IMPLEMENTATION_SUMMARY.md

---

**Status**: ⬜ Not Started | 🔄 In Progress | ✅ Complete

**Date Completed**: _______________

**Notes**:
_____________________________________________________________
_____________________________________________________________
_____________________________________________________________
